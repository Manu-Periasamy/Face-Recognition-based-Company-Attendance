<img src="/recognition_system/static/images/home.png" alt="drawing" width="200"/>


# Face Recognition based Company Attendance System
<!-- > Additional information or tagline
 -->
This project is a company attendance system that uses <b>facial anti-spoofing</b> and <b>recognition</b> to recognize employees and marks their entry and exit time in the database. The system effortlessly tracks time for employees with facial recognition, without human intervention or physical validation, as the system can detect and recognize faces autonomously.

## Getting started

A quick introduction of the minimal setup you need to get this project up & running in a <b>Linux environment</b>.

The first thing to do is to clone the repository:
```shell
git clone https://github.com/vansf07/Face-Recognition-based-Company-Attendance.git
cd Face-Recognition-based-Company-Attendance
```
Create a virtual environment to install dependencies in and activate it:
```shell
virtualenv venv --python=python3.8.10 
source venv/bin/activate 
pip install --upgrade pip==22.1 
```
Then install the dependanceis:
```shell
pip install -r requirements.txt 
```
Once pip has finished downloading the dependencies:
```shell
python manage.py runserver
```
And navigate to http://127.0.0.1:8000/.

## Admin Login
```bash
username: admin
password: rWN7fZ4R
```


## Users

### Admin
* Register a new Employee. Add photos to dataset via webcam soon after successful registration.
* View attendance of all employees on a particular day (through table and barplot for better comparison)
* View attendance of particular employee during selected duration (through table and barplot for better comparison)
* View daily statistics like number of employees present, total number of employees
* View weekly statistics like this week's attendance, last week's attendance (through lineplot)

### Employee
* Mark attendance in-time on company home page through face recognition
* Mark attendance out-time on company home page through face recognition
* View their own attendance (through table and barplot for better comparison)


## Implementation
[Flowchart](https://user-images.githubusercontent.com/75719373/170851759-29924808-e721-40f8-a3f2-816b1c2ebb71.png) 

### Tech Stack:
* <b>Django</b>: I used Django for the backend. The reason I chose Django is because of its ‘batteries included’ approach, which means that essentials like authentication, admin interfacing and managing temporary messages have all been included in the framework.
* <b>Bootstrap</b>: For the Front-end I’ve used Bootstrap to make my web application <b>responsive</b> and easy to navigate. 
* <b>OpenCV</b>: For the face recognition system itself, I have used Haar and LBPH. Face is detected using Haar Cascade, which is one of OpenCV’s most popular object detection algorithms and one of its main benefits is its speed.  
For face recognition, I’ve used LBPH, also provided by OpenCV through which it is possible to get great results because it is robust against monotonic grayscale transformations.  
Note: OpenCV may freeze due to compatibility isses with Linux but restarting the app will resolve the issue. 
* <b>dlib</b>: dlib is a C++ library with python bindings used to detect the face while adding a newly registered employee's photos to the training dataset. 
* <b>Matplotlib, Pandas, Numpy, Seaborn, Scipy</b>:  used for depicting employee attendance through tables, barplots as well as lineplots.

