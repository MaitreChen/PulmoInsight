# 📣Introduction

PulmoInsight is a Django-based system designed to provide a user-friendly platform for communication between patients and doctors, promoting transparency in treatment processes. This simple system focuses on facilitating effective interactions without incorporating extensive complexities.

---

🤔**Why called PulmoInsight？**

 "PulmoInsight" reflects the web system's focus on pulmonary health and its goal of providing clear and insightful communication between patients and doctors. 

* **Pulmo:** Refers to the lungs, highlighting the system's focus on pulmonary health. 
* **Insight:** Denotes the ability to gain an accurate and deep understanding of the lungs' condition, emphasizing that the system is more than just an image classification tool.

# 🎉Features

## Part1: Identity Management Module🆔

- **Login:** Secure access for users.
- **Registration:** Easy sign-up for new users.
- **Password Reset:** Convenient password recovery.

## Part2: Patient User Module😷

- **Main Interface:** Simple user dashboard.
- **Personal Information Center:** Manage personal basic data. (sex,age,etc)
- **Medical Records Upload:** Upload medical records. (pulmonary image,medical history,symptoms,etc)
- **History Query:** Access past medical records. (upload time,diagnosis status actions, etc)
- **Community Comments:** Engage with community for support and information sharing.

## Part3: Doctor User Module🧑‍⚕️

- **Lung X-ray Analysis:** Upload and Perform lung X-ray diagnoses.
- **Diagnostic Records Query:** Access patient diagnostic history. (diagnosis status/result/time, controversy status, etc)

# ✨Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

## Prerequisites

Ensure you have the following installed on your machine:

- Python 3.8
- pip (Python package installer)
- virtualenv (optional but recommended)

## Installation

1. **Clone the repository:**

   ```bash
   git clone git@github.com:MaitreChen/PulmoInsight.git
   cd PulmoInsight
   ```

2. **Create and activate a virtual environment:**

   ```bash
   conda create --name pulmoinsight-env python==3.x
   conda activate pulmoinsight-env
   ```

3. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```


## Usage

1. **Generate migration file and apply database migrations:**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
   
2. **Create a superuser (optional but recommended for admin access):**

   ```bash
   python manage.py createsuperuser
   ```

3. **To start the development server, run:**

   ```bash
   python manage.py runserver
   ```

   Then open your web browser and visit `http://127.0.0.1:8000/` to see the application in action.

# 🤝Contributing

We welcome contributions to PulmoInsight! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request.

Please ensure your code adheres to the existing code style~~

# 📞Contact

For any questions or suggestions about this project, welcome everyone to raise **issues**!

Also, please feel free to contact [hbchenstu@outlook.com](mailto:hbchenstu@outlook.com).

Thank you, wish you have a pleasant experience~~💓🧡💛💚💙💜