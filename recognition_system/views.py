from cv2 import VideoCapture
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.forms import CustomUserCreationForm
from recognition_system.forms import DateForm, UsernameAndDateForm, DateForm_2
from users.models import Profile
from datetime import datetime
from django.shortcuts import render
from users.models import Profile, Present, Time
from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import  HttpResponseRedirect
import sys
sys.path.append('/usr/local/lib/python3.8/site-packages')
import cv2
import dlib
import imutils
from imutils import face_utils
from imutils.face_utils import FaceAligner
from attendance.settings import BASE_DIR
import os
import face_recognition
import numpy
import matplotlib as plt
plt.use('Agg')
import datetime
from django_pandas.io import read_frame
from users.models import Present, Time
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
from matplotlib import rcParams
import math
from scipy.spatial import distance as dist
from django.views.decorators.cache import cache_control
from django.contrib.auth import logout


datasets = 'training_dataset'
haar_file = 'face_recognition_data/haarcascade_frontalface_default.xml'


# Create your views here.

# home page
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):
	return render(request, 'index.html')


# custom logout view
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login')
def custom_logout(request):
	print('Loggin out {}'.format(request.user))
	logout(request)
	print(request.user)
	return HttpResponseRedirect("/")


# register new employee
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login')
def register(request):
	if request.user.username!='admin':
		return redirect('not-authorised')
	if request.method=='POST':
		form=CustomUserCreationForm(request.POST)
		if form.is_valid():
			form.save() ### add employee to database
			id = form.cleaned_data.get('username')
			return redirect('create_dataset', id=id)
		else:
			return render(request, 'register.html', {'form' : form})


	else:
		form=CustomUserCreationForm()
	return render(request, 'register.html', {'form' : form})



# page for unauthorised attempts
@login_required
def not_authorised(request):
	return render(request,'not_authorized.html')




# dashboard
@cache_control(no_cache=True, must_revalidate=True, no_store=True, )
@login_required(login_url='login')
def dashboard(request):
	if( request.user.username =='admin'):
		print("admin")
		total_num_of_emp=total_number_employees()
		emp_present_today=employees_present_today()
		this_week_emp_count_vs_date()
		last_week_emp_count_vs_date()
		return render(request, 'admin_dashboard.html',
		{'total_num_of_emp' : total_num_of_emp, 'emp_present_today': emp_present_today})
	else:
		print("not admin")
		return render(request,'employee_dashboard.html')




# create dataset for newly registered employee
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login')
def create_dataset(request, id):
	if(os.path.exists('training_dataset/{}/'.format(id))==False):
		os.makedirs('training_dataset/{}/'.format(id))
	directory='training_dataset/{}/'.format(id)
	detector = dlib.get_frontal_face_detector()
	predictor = dlib.shape_predictor('face_recognition_data/shape_predictor_68_face_landmarks.dat')
	fa = FaceAligner(predictor , desiredFaceWidth = 256)

	vs = cv2.VideoCapture(0)

	# sampleNum = 0
	count_image = 0

	# loop over the frames in the video stream
	while(True):
		if not vs.isOpened():
			vs.open(0)
		# grab the frame from the threaded video stream, resize it to
		# have a maximum width of 400 pixels, and convert it to
		# grayscale
		(ret,frame) = vs.read()
		frame = imutils.resize(frame, width = 400)
		if ret == False:
			webcam = cv2.VideoCapture(0)
			continue
		if ret== True:
			height, width = frame.shape[:2]
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

			# detect faces in the grayayscale frame
			rects = detector(gray, 0)
			if len(rects) > 0:
				faceAligned = fa.align(frame, gray, rects[0])
				image_name = directory + str(count_image) + ".jpg"
				# save image
				cv2.imwrite(image_name, faceAligned)
				count_image += 1
				if count_image > 100:
					break


			# loop over the face detections
			for rect in rects:
				(x,y,w,h) = face_utils.rect_to_bb(rect)
				cv2.rectangle(frame, (x, y), (x+w, y+h), (0,0,255), 1)

			# show the frame
			cv2.imshow("Frame", frame)
			key = cv2.waitKey(1) & 0xFF
			# if the `q` key was pressed, break from the loop
			if key == ord("q"):
				break

	#Stoping the videostream
	vs.release()
	# destroying all the windows
	cv2.destroyAllWindows()
	cv2.waitKey(1)
	return redirect('dashboard')





# mark attendance entry time
def mark_your_attendance_in(request):
	EYES_CLOSED_SECONDS = 1
	closed_count = 0
	open_count = 0

	webcam = VideoCapture(1)
	# check for blink
	process = True
	while True:
		if not webcam.isOpened():
			webcam.open(0)
		ret, frame = webcam.read(0)
		time = 0

		if ret == False:
			webcam = cv2.VideoCapture(0)
			continue
		if ret == True:
			# get it into the correct format
			small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
			rgb_small_frame = small_frame[:, :, ::-1]

			# get the correct face landmarks

			if process:
				face_landmarks_list = face_recognition.face_landmarks(rgb_small_frame)

				# get eyes
				for face_landmark in face_landmarks_list:
					left_eye = face_landmark['left_eye']
					right_eye = face_landmark['right_eye']


					color = (255,0,0)
					thickness = 2

					cv2.rectangle(small_frame, left_eye[0], right_eye[-1], color, thickness)
					cv2.imshow('Please Blink Within 30 Seconds', frame)

					cv2.waitKey(1)
					ear_left = get_ear(left_eye)
					ear_right = get_ear(right_eye)

					closed = ear_left < 0.2 and ear_right < 0.2

					if (closed):
						closed_count += 1
					else:
						closed_count = 0
						open_count +=1
			
			cv2.imshow('Please Blink Within 30 Seconds', frame)
			cv2.waitKey(1)
			process = not process
			key = cv2.waitKey(1) & 0xFF
			if key == ord("q"):
				break

			# if blink is detected
			if (closed_count>=1):
				cv2.putText(frame, 'Blink Successful', 
				(50,50), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
				break
			
			# if blink not detected, refresh page
			elif open_count>300:
				cv2.destroyAllWindows()
				cv2.waitKey(1)

				cv2.putText(frame, 'Blink Not Detected!', 
				(50,50), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))			
				return redirect('home')
		else:
			print('Could not open webcam. Please restart app')


	# recognizing face if blink successful
	present = dict()

	print('Recognizing Face Please Be in sufficient Lights...')

	# Create a list of images and a list of corresponding names
	(images, labels, names, id) = ([], [], {}, 0)
	for (subdirs, dirs, files) in os.walk(datasets):
		for subdir in dirs:
			present[subdir] = False
			names[id] = subdir
			subjectpath = os.path.join(datasets, subdir)
			for filename in os.listdir(subjectpath):
				path = subjectpath + '/' + filename
				label = id
				images.append(cv2.imread(path, 0))
				labels.append(int(label))
			id += 1
	(width, height) = (130, 100)

	# Create a Numpy array from the two lists above
	(images, labels) = [numpy.array(lis) for lis in [images, labels]]

	# OpenCV trains a model from the images
	model = cv2.face.LBPHFaceRecognizer_create()
	model.train(images, labels)
	
	# Part 2: Use Haar Cascade Classifier on camera stream
	face_cascade = cv2.CascadeClassifier(haar_file)

	while True:
		(_, im) = webcam.read()
		if _ == True:
			gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
			faces = face_cascade.detectMultiScale(gray, 1.3, 5)
			for (x, y, w, h) in faces:
				cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2)
				face = gray[y:y + h, x:x + w]
				face_resize = cv2.resize(face, (width, height))
				# Try to recognize the face
				prediction = model.predict(face_resize)
				cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 3)
				# if employee recognized
				if prediction[1]<500:
					present[names[prediction[0]]] = True
					cv2.putText(im, '% s - %.0f' % (names[prediction[0]], prediction[1]), (x-10, y-10),
					cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
				else:
					cv2.putText(im, 'not recognized',
					(x-10, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))

			cv2.imshow('OpenCV', im)
			if (cv2.waitKey(1)== ord('q')):
				break
	# destroying all the windows
	webcam.release()
	cv2.destroyAllWindows()
	cv2.waitKey(1)
	update_attendance_in_db_in(present)
	return redirect('home')




# updating entry attendance in database
def update_attendance_in_db_in(present):
	today=datetime.date.today()
	time=datetime.datetime.now()
	for person in present:
		user=Profile.objects.get(username=person)
		# if person is present today
		try:
			qs=Present.objects.get(user=user,date=today)
		except:
			qs= None
		# if person is marking attendance for the first time today,
		# mark them as present if present, and absent if not
		if qs is None:
			if present[person]==True:
						a=Present(user=user,date=today,present=True)
						a.save()
			else:
				a=Present(user=user,date=today,present=False)
				a.save()
		# if person is present today, update their in-time
		else:
			if present[person]==True:
				qs.present=True
				qs.save(update_fields=['present'])
		if present[person]==True:
			a=Time(user=user,date=today,time=time, out=False)
			a.save()




# mark exit attendance
def mark_your_attendance_out(request):
	EYES_CLOSED_SECONDS = 1
	closed_count = 0
	open_count = 0

	webcam = cv2.VideoCapture(0)
	# check for blinking
	process = True
	while True:
		if not webcam.isOpened():
			webcam.open(0)
		ret, frame = webcam.read(0)
		# if webcam not opened
		if ret == False:
			webcam = cv2.VideoCapture(1)
			continue
		# if webcam opened successfully
		if ret == True:
			# resize frame
			small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
			rgb_small_frame = small_frame[:, :, ::-1]

			# get the correct face landmarks

			if process:
				face_landmarks_list = face_recognition.face_landmarks(rgb_small_frame)

				# get eyes
				for face_landmark in face_landmarks_list:
					left_eye = face_landmark['left_eye']
					right_eye = face_landmark['right_eye']
					color = (255,0,0)
					thickness = 2
					cv2.rectangle(small_frame, left_eye[0], right_eye[-1], color, thickness)
					cv2.imshow('Please Blink', frame)
					cv2.waitKey(1)
					ear_left = get_ear(left_eye)
					ear_right = get_ear(right_eye)

					closed = ear_left < 0.2 and ear_right < 0.2

					if (closed):
						closed_count += 1
					else:
						closed_count = 0
						open_count += 1

			cv2.imshow('Please Blink', frame)
			cv2.waitKey(1)
			process = not process
			key = cv2.waitKey(1) & 0xFF
			if key == ord("q"):
				break
			# if blink was detected
			if (closed_count>=1):
				cv2.putText(frame, 'Blink Successful', 
				(50,50), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
				break
			# if blink not detected
			elif open_count>300:
				webcam.release()
				cv2.destroyAllWindows()
				cv2.waitKey(1)
				cv2.putText(frame, 'Blink Not Detected!', 
				(50,50), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))			
				return redirect('home')
		else:
			print('Could not open webcam! Please restart app')

	# Recognizing faces
	present = dict()

	(images, labels, names, id) = ([], [], {}, 0)
	for (subdirs, dirs, files) in os.walk(datasets):
		for subdir in dirs:
			present[subdir] = False
			names[id] = subdir
			subjectpath = os.path.join(datasets, subdir)
			for filename in os.listdir(subjectpath):
				path = subjectpath + '/' + filename
				label = id
				images.append(cv2.imread(path, 0))
				labels.append(int(label))
			id += 1
	(width, height) = (130, 100)

	# Create a Numpy array from the two lists above
	(images, labels) = [numpy.array(lis) for lis in [images, labels]]

	# OpenCV trains a model from the images
	model = cv2.face.LBPHFaceRecognizer_create()
	model.train(images, labels)

	# Part 2: Use Haar Cascade Classifier on camera stream
	face_cascade = cv2.CascadeClassifier(haar_file)

	while True:
		(_, im) = webcam.read()
			
		if _ == True:
			gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
			faces = face_cascade.detectMultiScale(gray, 1.3, 5)
			for (x, y, w, h) in faces:
				cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2)
				face = gray[y:y + h, x:x + w]
				face_resize = cv2.resize(face, (width, height))
				# Try to recognize the face
				prediction = model.predict(face_resize)
				cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 3)
				# if employee recognized
				if prediction[1]<500:
					present[names[prediction[0]]] = True
					cv2.putText(im, '% s - %.0f' % (names[prediction[0]], prediction[1]), (x-10, y-10),
					cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
				else:
					cv2.putText(im, 'not recognized',
					(x-10, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))

			cv2.imshow('OpenCV', im)
			if (cv2.waitKey(1)== ord('q')):
				break
	# destroying all the windows
	webcam.release()
	cv2.destroyAllWindows()
	cv2.waitKey(1)
	update_attendance_in_db_out(present)
	return redirect('home')




# update exit attendance in database
def update_attendance_in_db_out(present):
	today=datetime.date.today()
	time=datetime.datetime.now()
	for person in present:
		user=Profile.objects.get(username=person)
		if present[person]==True:
			a=Time(user=user,date=today,time=time, out=True)
			a.save()



def check_validity_times(times_all):
	if(len(times_all)>0):
		sign=times_all.first().out
	else:
		sign=True
	times_in=times_all.filter(out=False)
	times_out=times_all.filter(out=True)
	if(len(times_in)!=len(times_out)):
		sign=True
	new_break_hours=0
	if(sign==True):
			check=False
			new_break_hours=0
			return (check,new_break_hours)
	prev=True
	prev_time=times_all.first().time

	for obj in times_all:
		curr=obj.out
		if(curr==prev):
			check=False
			new_break_hours=0
			return (check,new_break_hours)
		if(curr==False):
			curr_time=obj.time
			to=curr_time
			ti=prev_time
			break_time=((to-ti).total_seconds())/3600
			new_break_hours+=break_time


		else:
			prev_time=obj.time

		prev=curr

	return (True,new_break_hours)



# converting hours to minutes
def convert_hours_to_hours_mins(hours):
	h=int(hours)
	hours-=h
	m=hours*60
	m=math.ceil(m)
	return str(str(h)+ " hr " + str(m) + "  min")



def hours_vs_date_given_employee(present_qs,time_qs,admin=True):
	register_matplotlib_converters()
	df_hours=[]
	df_break_hours=[]
	qs=present_qs
	for obj in qs:
		date=obj.date
		times_in=time_qs.filter(date=date).filter(out=False).order_by('time')
		times_out=time_qs.filter(date=date).filter(out=True).order_by('time')
		times_all=time_qs.filter(date=date).order_by('time')
		obj.time_in=None
		obj.time_out=None
		obj.hours=0
		obj.break_hours=0
		if (len(times_in)>0):
			obj.time_in=times_in.first().time

		if (len(times_out)>0):
			obj.time_out=times_out.last().time

		if(obj.time_in is not None and obj.time_out is not None):
			ti=obj.time_in
			to=obj.time_out
			hours=((to-ti).total_seconds())/3600
			obj.hours=hours
		else:
			obj.hours=0

		(check,new_break_hours)= check_validity_times(times_all)
		if check:
			obj.break_hours=new_break_hours
		else:
			obj.break_hours=0

		# hours_worked = total_hours - break_hours
		df_hours.append(obj.hours - obj.break_hours) 	
		df_break_hours.append(obj.break_hours)
		obj.hours=convert_hours_to_hours_mins(obj.hours)
		obj.break_hours=convert_hours_to_hours_mins(obj.break_hours)

	df = read_frame(qs)
	df["Hours Worked"]=df_hours
	df["break_hours"]=df_break_hours
	sns.set_palette(sns.light_palette("seagreen"))
	sns.barplot(data=df,x='date',y='Hours Worked')
	plt.xlabel("Date")
	plt.xticks(rotation='vertical')
	rcParams.update({'figure.autolayout': True})
	plt.tight_layout()
	if(admin):
		plt.savefig('./recognition_system/static/attendance_graphs/hours_vs_date/1.png')
		plt.close()
	else:
		plt.savefig('./recognition_system/static/attendance_graphs/employee_login/1.png')
		plt.close()
	return qs





def hours_vs_employee_given_date(present_qs,time_qs):
	register_matplotlib_converters()
	df_hours=[]
	df_break_hours=[]
	df_username=[]
	df_name=[]
	df_department=[]
	qs=present_qs

	for obj in qs:
		user=obj.user
		times_in=time_qs.filter(user=user).filter(out=False)
		times_out=time_qs.filter(user=user).filter(out=True)
		times_all=time_qs.filter(user=user)
		obj.time_in=None
		obj.time_out=None
		obj.hours=0
		obj.hours=0
		if (len(times_in)>0):
			obj.time_in=times_in.first().time
		if (len(times_out)>0):
			obj.time_out=times_out.last().time
		if(obj.time_in is not None and obj.time_out is not None):
			ti=obj.time_in
			to=obj.time_out
			hours=((to-ti).total_seconds())/3600
			obj.hours=hours
		else:
			obj.hours=0
		(check,new_break_hours)= check_validity_times(times_all)
		if check:
			obj.break_hours=new_break_hours


		else:
			obj.break_hours=0


		df_hours.append(obj.hours - obj.break_hours)
		df_department.append(user.department)
		df_username.append(user.username)
		df_name.append(user.first_name + ' ' + user.last_name)
		df_break_hours.append(obj.break_hours)
		obj.hours=convert_hours_to_hours_mins(obj.hours)
		obj.break_hours=convert_hours_to_hours_mins(obj.break_hours)



	df = read_frame(qs)
	df['Hours Worked']=df_hours
	df['Employee Name']=df_name
	df["break_hours"]=df_break_hours
	df["Department"]=df_department

	sns.set_palette(sns.light_palette("seagreen"))
	sns.barplot(data=df,x='Employee Name',y='Hours Worked')
	plt.xticks(rotation='vertical')
	rcParams.update({'figure.autolayout': True})
	plt.tight_layout()
	plt.savefig('./recognition_system/static/attendance_graphs/hours_vs_employee/1.png')
	plt.close()
	return qs



@cache_control(no_cache=True, must_revalidate=True, no_store=True, )
@login_required(login_url='login')
def view_attendance_date(request):
	if request.user.username!='admin':
		return redirect('not-authorised')
	qs=None
	time_qs=None
	present_qs=None


	if request.method=='POST':
		form=DateForm(request.POST)
		if form.is_valid():
			date=form.cleaned_data.get('date')
			print("date:"+ str(date))
			time_qs=Time.objects.filter(date=date)
			present_qs=Present.objects.filter(date=date)
			if(len(time_qs)>0 or len(present_qs)>0):
				qs=hours_vs_employee_given_date(present_qs,time_qs)
				return render(request, 'attendance_date.html', {'form' : form,'qs' : qs })
			else:
				messages.warning(request, f'No records for selected date.')
				return redirect('view_attendance_date')

	else:
			form=DateForm()
			return render(request,'attendance_date.html', {'form' : form, 'qs' : qs})



@cache_control(no_cache=True, must_revalidate=True, no_store=True, )
@login_required(login_url='login')
def view_attendance_employee(request):
	if request.user.username!='admin':
		return redirect('not-authorised')
	time_qs=None
	present_qs=None
	qs=None

	if request.method=='POST':
		form=UsernameAndDateForm(request.POST)
		if form.is_valid():
			username=form.cleaned_data.get('username')
			if Profile.objects.filter(username=username).exists():
				u=Profile.objects.get(username=username)

				time_qs=Time.objects.filter(user=u)
				present_qs=Present.objects.filter(user=u)
				date_from=form.cleaned_data.get('date_from')
				date_to=form.cleaned_data.get('date_to')

				if date_to < date_from:
					messages.warning(request, f'Invalid date selection.')
					return redirect('view_attendance_employee')
				else:


					time_qs=time_qs.filter(date__gte=date_from).filter(date__lte=date_to).order_by('-date')
					present_qs=present_qs.filter(date__gte=date_from).filter(date__lte=date_to).order_by('-date')

					if (len(time_qs)>0 or len(present_qs)>0):
						qs=hours_vs_date_given_employee(present_qs,time_qs,admin=True)
						return render(request,'attendance_employee.html', {'form' : form, 'qs' :qs})
					else:
						messages.warning(request, f'No records for selected duration.')
						return redirect('view_attendance_employee')
			else:
				print("invalid username")
				messages.warning(request, f'Username not found found.')
				return redirect('view_attendance_employee')
	else:
			form=UsernameAndDateForm()
			return render(request,'attendance_employee.html', {'form' : form, 'qs' :qs})




@cache_control(no_cache=True, must_revalidate=True, no_store=True, )
@login_required(login_url='login')
def employee_view_attendance(request):
	if request.user.username=='admin':
		return redirect('not-authorised')
	qs=None
	time_qs=None
	present_qs=None
	if request.method=='POST':
		form=DateForm_2(request.POST)
		if form.is_valid():
			u=request.user
			time_qs=Time.objects.filter(user=u)
			present_qs=Present.objects.filter(user=u)
			date_from=form.cleaned_data.get('date_from')
			date_to=form.cleaned_data.get('date_to')
			if date_to < date_from:
					messages.warning(request, f'Invalid date duration.')
					return redirect('employee_view_employee_attendance')
			else:
					time_qs=time_qs.filter(date__gte=date_from).filter(date__lte=date_to).order_by('-date')
					present_qs=present_qs.filter(date__gte=date_from).filter(date__lte=date_to).order_by('-date')

					if (len(time_qs)>0 or len(present_qs)>0):
						qs=hours_vs_date_given_employee(present_qs,time_qs,admin=False)
						return render(request,'employee_view_attendance.html', {'form' : form, 'qs' :qs})
					else:

						messages.warning(request, f'No records for selected duration.')
						return redirect('employee_view_employee_attendance')
	else:


			form=DateForm_2()
			return render(request,'employee_view_attendance.html', {'form' : form, 'qs' :qs})




def get_ear(eye):

	# compute the euclidean distances between the two sets of
	# vertical eye landmarks (x, y)-coordinates
	A = dist.euclidean(eye[1], eye[5])
	B = dist.euclidean(eye[2], eye[4])

	# compute the euclidean distance between the horizontal
	# eye landmark (x, y)-coordinates
	C = dist.euclidean(eye[0], eye[3])

	# compute the eye aspect ratio
	ear = (A + B) / (2.0 * C)

	# return the eye aspect ratio
	return ear



# returns total number of employees in company
def total_number_employees():
	qs=Profile.objects.all()
	# -1 to subtract admin
	return (len(qs) -1)


# returns employees present today
def employees_present_today():
	today=datetime.date.today()
	qs=Present.objects.filter(date=today).filter(present=True)
	return len(qs)


def this_week_emp_count_vs_date():
	today=datetime.date.today()
	some_day_last_week=today-datetime.timedelta(days=7)
	monday_of_last_week=some_day_last_week-  datetime.timedelta(days=(some_day_last_week.isocalendar()[2] - 1))
	monday_of_this_week = monday_of_last_week + datetime.timedelta(days=7)
	qs=Present.objects.filter(date__gte=monday_of_this_week).filter(date__lte=today)
	str_dates=[]
	emp_count=[]
	str_dates_all=[]
	emp_cnt_all=[]
	cnt=0

	for obj in qs:
		date=obj.date
		str_dates.append(str(date))
		qs=Present.objects.filter(date=date).filter(present=True)
		emp_count.append(len(qs))


	while(cnt<5):

		date=str(monday_of_this_week+datetime.timedelta(days=cnt))
		cnt+=1
		str_dates_all.append(date)
		if(str_dates.count(date))>0:
			idx=str_dates.index(date)

			emp_cnt_all.append(emp_count[idx])
		else:
			emp_cnt_all.append(0)

	df=pd.DataFrame()
	df["Date"]=str_dates_all
	df["Number of employees"]=emp_cnt_all

	# Create an array with the colors you want to use
	colors = ["#5a7875"]
	
	
	sns.set_palette(sns.color_palette(colors))
	sns.lineplot(data=df,x='Date',y='Number of employees', linewidth = 1.5)
	plt.savefig('./recognition_system/static/attendance_graphs/this_week/1.png')
	plt.close()



def last_week_emp_count_vs_date():
	today=datetime.date.today()
	some_day_last_week=today-datetime.timedelta(days=7)
	monday_of_last_week=some_day_last_week-  datetime.timedelta(days=(some_day_last_week.isocalendar()[2] - 1))
	monday_of_this_week = monday_of_last_week + datetime.timedelta(days=7)
	qs=Present.objects.filter(date__gte=monday_of_last_week).filter(date__lt=monday_of_this_week)
	str_dates=[]
	emp_count=[]


	str_dates_all=[]
	emp_cnt_all=[]
	cnt=0


	for obj in qs:
		date=obj.date
		str_dates.append(str(date))
		qs=Present.objects.filter(date=date).filter(present=True)
		emp_count.append(len(qs))


	while(cnt<5):

		date=str(monday_of_last_week+datetime.timedelta(days=cnt))
		cnt+=1
		str_dates_all.append(date)
		if(str_dates.count(date))>0:
			idx=str_dates.index(date)

			emp_cnt_all.append(emp_count[idx])

		else:
			emp_cnt_all.append(0)

	df=pd.DataFrame()
	df["Date"]=str_dates_all
	df["Number of employees"]=emp_cnt_all


	colors = ["#5a7875"]
	sns.set_palette(sns.color_palette(colors))
	sns.lineplot(data=df,x='Date',y='Number of employees',linewidth = 1.5)
	plt.savefig('./recognition_system/static/attendance_graphs/last_week/1.png')
	plt.close()