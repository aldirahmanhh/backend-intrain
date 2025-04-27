<div align=justify>
  <img src="https://img.shields.io/badge/inTraini.ai-6471e5?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/markdown-%23000000.svg?style=for-the-badge&logo=markdown&logoColor=white"/>
</div>

<div align=center>

  <h1>inTrain.ai</h1>

  <img src="https://github.com/intrain-ai/.github/blob/main/assets/Banner%20-%20intrain.ai.png"/>
</div>
<br>
<div align=center>
    <img src="https://img.shields.io/badge/Python-3670A0?&logo=python&logoColor=ffdd54"/>
    <img src="https://img.shields.io/badge/Flask-%23000.svg?&logo=flask&logoColor=white"/>
    <img src="https://img.shields.io/badge/Docker-%230db7ed.svg?&logo=docker&logoColor=white"/>
    <img src="https://img.shields.io/badge/Google_Cloud-%234285F4.svg?&logo=google-cloud&logoColor=white"/>
    <img src="https://img.shields.io/badge/MySQL-4479A1.svg?&logo=mysql&logoColor=white"/>
    <h3>Back-End Server and API Services Documentation</h3>
</div>

---

### Repository Overview

<p align=justify>
This repository contains of backend server designed for various specific functions in a single ecosystem for the inTrain.ai application. The purpose of this repository is to provide an organized 
structure for the development, maintenance, and documentation of inTrain.ai server.
</p>

### Tech Stacks

- **Programming Language**: Python
- **Framework**: Flask
- **Relational Database**: MySQL

### API Services Documentation

---
**Important Notes**

The API endpoints currently documented with the placeholder ```{base}``` point to the local development server ```http://localhost:5000```. When the backend has been deployed, the mobile development team should update the domain to the production URL provided by the cloud computing and backend team.

#### Login API

---

- Method: ```POST```

- URL
```bash
{base}/api/v1/auth/user/login
```

- Request Body:
```json
{
    "username": "admin",
    "password": "admin123"
}
```

- Response:
```json
{
    "message": "Login successful.",
    "user": {
        "created_at": "2025-04-26T07:59:18",
        "email": "admin@intrain.ai",
        "id": "5f684a9c-2bcb-4e40-b176-03277860a9f7",
        "name": "Admin",
        "username": "admin"
    }
}
```

#### Register API

---

- Method: ```POST```

- URL
```bash
{base}/api/v1/auth/user/register
```

- Request Body:
```json
{
    "username":"admin2",
    "password":"admin234",
    "name":"Admin2",
    "email":"admin2@intrain.ai"
}
```

- Response:
```json
{
    "message": "Registration successful."
}
```

#### Update API

---

- Method: ```PUT```

- URL
```bash
{base}/api/v1/auth/user/update
```

- Request Body:
```json
{
    "user_id":"7faca6b6-8604-4d28-9d07-2ade7d70b4ae",
    "username":"admin2",
    "password":"admin2newpass",
    "name":"Admin2",
    "email":"admin2@intrain.ai"
}
```

- Response:
```json
{
    "message": "User data updated successfully."
}
```
#### Get All HR Level API

---

- Method: ```GET```

- URL
```bash
{base}/api/v1/feature/chat/hr_levels
```

- Response:
```json
[
    {
        "description": "A beginner friendly",
        "difficulty_rank": 1,
        "id": 1,
        "name": "Easy"
    },
    {
        "description": "Need a bit of experiences",
        "difficulty_rank": 2,
        "id": 2,
        "name": "Normal"
    },
    {
        "description": "Highly experienced HR",
        "difficulty_rank": 3,
        "id": 3,
        "name": "Hard"
    }
]
```


#### Inintialize Chat with HR Bot API

---

- Method: ```POST```

- URL
```bash
{base}/api/v1/feature/interview/chat
```

- Request Body:
```json
{
    "user_id":"5f684a9c-2bcb-4e40-b176-03277860a9f7",
    "hr_level_id":1,
    "job_type":"BackEnd Engineer"
}
```

- Response:
```json
{
    "response": {
        "question_number": 1,
        "question_text": "Please introduce yourself: your name, current role, and how many years of experience you have.",
        "type": "question"
    },
    "session_id": "2f372196-e2fb-49bc-a937-eb546abe554d"
}
```

#### Continuous Chat with HR Bot API

---

- Method: ```POST```

- URL
```bash
{base}/api/v1/feature/interview/chat
```

- Request Body (Use the same Request Body):
```json
{
    "session_id":"2f372196-e2fb-49bc-a937-eb546abe554d" (From initialize chat),
    "message":"Hello, my name is Admin, my current role is a Freelance BackEnd Engineer, and i have 2 years of experiences" (User chat input)
}
```
- Response (HR Bot will Response Every message):
```json
{
    "response": {
        "question_number": 2 (Randomly Generated),
        "question_text": "Can you describe a challenging backend project you worked on and how you overcame the obstacles you faced?" (Randomly Generated),
        "type": "question"
    },
    "session_id": "2f372196-e2fb-49bc-a937-eb546abe554d"
}
```

- Response (HR Bot will Ended the Chat with Evaluation):
```json
{
    "evaluation": {
        "evaluated_at": "2025-04-26T16:20:00",
        "id": "96e149e2-bf58-4dc3-b387-acde31aed338",
        "recommendations": [
            "Candidate needs to provide more detailed and comprehensive answers to demonstrate technical proficiency.",
            "Candidate should elaborate on specific technologies, tools, and methodologies used in backend development.",
            "Candidate needs to provide more concrete examples and explain the reasoning behind their choices."
        ] (Generated by AI),
        "score": 3 (AI will Score 1-10),
        "session_id": "2f372196-e2fb-49bc-a937-eb546abe554d"
    },
    "session_id": "2f372196-e2fb-49bc-a937-eb546abe554d"
}
```

#### Get All User Chat History API

---

- Method: ```GET```

- URL
```bash
{base}/api/v1/feature/interview/chat/history/<user_id>
```

- Request URL
```bash
{base}/api/v1/feature/interview/chat/history/5f684a9c-2bcb-4e40-b176-03277860a9f7
```

- Response:
```json
{
    "chats": [
        {
            "hr_level_id": 1,
            "job_type": "BackEnd Engineer",
            "last_message": "Describe your experience with different types of databases (e.g., relational, NoSQL). What are the pros and cons of each, and when would you choose one over the other?",
            "last_message_at": "2025-04-26T16:23:55",
            "session_id": "a06b2ce6-043f-4ddb-b123-dbced279a4a8",
            "started_at": "2025-04-26T16:22:40"
        },
        {
            "hr_level_id": 1,
            "job_type": "BackEnd Engineer",
            "last_message": "Using a tools in web and AI",
            "last_message_at": "2025-04-26T16:22:25",
            "session_id": "2f372196-e2fb-49bc-a937-eb546abe554d",
            "started_at": "2025-04-26T16:13:33"
        },
        ...
    ],
    "user_id": "5f684a9c-2bcb-4e40-b176-03277860a9f7"
}
```
#### Get Chat Session History API

---

- Method: ```GET```

- URL
```bash
{base}/api/v1/feature/interview/chat/<session_id>/history
```

- Request URL
```bash
{base}/api/v1/feature/interview/chat/fdd67809-a48f-4670-9674-33143cb55c80/history
```

- Response:
```json
{
    "history": [
        {
            "content": {
                "question_number": 1,
                "question_text": "Please introduce yourself: your name, current role, and how many years of experience you have.",
                "type": "question"
            },
            "sender": "bot",
            "sent_at": "2025-04-26T14:18:31"
        },
        {
            "content": {
                "text": "My name is John, no have roles and experiences"
            },
            "sender": "user",
            "sent_at": "2025-04-26T14:19:17"
        },
        ...
    ],
    "session_id": "fdd67809-a48f-4670-9674-33143cb55c80"
}
```

#### Upload CV API

---

- Method: ```POST```

<div align="center">
  
![Screenshot 2025-04-27 001608](https://github.com/user-attachments/assets/c7cb1535-a7d5-4e80-85ca-3875ba1827bd)

</div>

- URL
```bash
{base}/api/v1/feature/cv/upload
```

- Response:
```json
{
    "review": {
        "ats_passed": true,
        "id": "fef6782e-3e57-4aaa-a503-e8b60ea51300",
        "overall_feedback": "The CV is well-structured and contains relevant information. It showcases a strong academic background and practical experience in software engineering, machine learning, and cloud computing. The use of keywords is good, and the descriptions of experiences and projects are detailed enough to be understood by an ATS. However, some sections can be improved for clarity and impact, especially the profile summary and the formatting across different sections.",
        "reviewed_at": "2025-04-26T17:14:39",
        "submission_id": "d351bde3-daec-41ee-8481-c75675be6be4"
    },
    "sections": [
        {
            "feedback": "The profile summary is a good start, but can be improved by quantifying achievements and being more specific about your contributions and the impact you've made. Highlight your key skills and tailor it to the specific job description you are applying for.",
            "id": "9dc1ef17-e068-43b3-92bd-448f4dd3f54c",
            "needs_improvement": true,
            "review_id": "fef6782e-3e57-4aaa-a503-e8b60ea51300",
            "section": "profile_summary"
        },
        {
            "feedback": "The education section is well-formatted and includes relevant coursework. The GPA is also a plus. Consider adding specific projects done during these courses if they are directly related to the jobs you're applying to.",
            "id": "fa7f14f2-b186-445d-b849-01c4286976f3",
            "needs_improvement": false,
            "review_id": "fef6782e-3e57-4aaa-a503-e8b60ea51300",
            "section": "education"
        },
        {
            "feedback": "The experience section is detailed and provides a good overview of your responsibilities and accomplishments. Use action verbs to start each bullet point. Quantify accomplishments whenever possible (e.g., \"Reduced server costs by X%...\").",
            "id": "693d57b8-9122-448d-bacd-1978e3a00c7b",
            "needs_improvement": false,
            "review_id": "fef6782e-3e57-4aaa-a503-e8b60ea51300",
            "section": "experience"
        },
        {
            "feedback": "The skills section is comprehensive and covers a wide range of relevant technologies. Consider categorizing the skills (e.g., \"Front-end\", \"Back-end\", \"Cloud\", \"Data Science\") for better readability. Ensure the listed skills align with the job description.",
            "id": "225a21c3-adc3-4da0-88ac-130b907ef40f",
            "needs_improvement": false,
            "review_id": "fef6782e-3e57-4aaa-a503-e8b60ea51300",
            "section": "skills"
        },
        {
            "feedback": "The certification section is well-formatted and includes the expiration dates, which is great. Keep them updated.",
            "id": "0d7954fa-a5a5-4924-a8c2-73c4fd627d6e",
            "needs_improvement": false,
            "review_id": "fef6782e-3e57-4aaa-a503-e8b60ea51300",
            "section": "certification"
        },
        {
            "feedback": "The portfolio section is clear. Ensure the GitHub link is working and showcases your best projects. Consider adding a brief description of each project on your GitHub profile.",
            "id": "67d7b526-0648-4b26-9132-d8773fadf791",
            "needs_improvement": false,
            "review_id": "fef6782e-3e57-4aaa-a503-e8b60ea51300",
            "section": "portfolio"
        }
    ],
    "submission": {
        "file_name": "my_cv.pdf",
        "file_type": "pdf",
        "file_url": "uploads\\5c3b3e3d-d116-4373-8a71-865ca19f409e.pdf",
        "id": "d351bde3-daec-41ee-8481-c75675be6be4",
        "uploaded_at": "2025-04-26T17:14:34",
        "user_id": "7faca6b6-8604-4d28-9d07-2ade7d70b4ae"
    }
}
```

---

#### Get One CV Submission History API

---

- Method: ```GET```

- URL
```bash
{base}/api/v1/feature/cv/history/<submission_id>
```

- Request URL
```bash
{base}/api/v1/feature/cv/history/d351bde3-daec-41ee-8481-c75675be6be4
```

- Response:
```json
{
    "submission": {
        "file_name": "my_cv.pdf",
        "file_type": "pdf",
        "file_url": "uploads\\5c3b3e3d-d116-4373-8a71-865ca19f409e.pdf",
        "id": "d351bde3-daec-41ee-8481-c75675be6be4",
        "uploaded_at": "2025-04-26T17:14:34",
        "user_id": "7faca6b6-8604-4d28-9d07-2ade7d70b4ae"
    }
}
```

#### List CV Reviews History API

---

- Method: ```GET```

- URL
```bash
{base}/api/v1/feature/cv/history/user/<user_id>/reviews
```

- Request URL
```bash
{base}/api/v1/feature/cv/history/user/7faca6b6-8604-4d28-9d07-2ade7d70b4ae/reviews
```

- Response:
```json
[
    {
        "review": {
            "ats_passed": true,
            "id": "fef6782e-3e57-4aaa-a503-e8b60ea51300",
            "overall_feedback": "The CV is well-structured and contains relevant information. It showcases a strong academic background and practical experience in software engineering, machine learning, and cloud computing. The use of keywords is good, and the descriptions of experiences and projects are detailed enough to be understood by an ATS. However, some sections can be improved for clarity and impact, especially the profile summary and the formatting across different sections.",
            "reviewed_at": "2025-04-26T17:14:39",
            "submission_id": "d351bde3-daec-41ee-8481-c75675be6be4"
        },
        "sections": [
            {
                "feedback": "The certification section is well-formatted and includes the expiration dates, which is great. Keep them updated.",
                "id": "0d7954fa-a5a5-4924-a8c2-73c4fd627d6e",
                "needs_improvement": false,
                "review_id": "fef6782e-3e57-4aaa-a503-e8b60ea51300",
                "section": "certification"
            },
            {
                "feedback": "The skills section is comprehensive and covers a wide range of relevant technologies. Consider categorizing the skills (e.g., \"Front-end\", \"Back-end\", \"Cloud\", \"Data Science\") for better readability. Ensure the listed skills align with the job description.",
                "id": "225a21c3-adc3-4da0-88ac-130b907ef40f",
                "needs_improvement": false,
                "review_id": "fef6782e-3e57-4aaa-a503-e8b60ea51300",
                "section": "skills"
            },
            {
                "feedback": "The portfolio section is clear. Ensure the GitHub link is working and showcases your best projects. Consider adding a brief description of each project on your GitHub profile.",
                "id": "67d7b526-0648-4b26-9132-d8773fadf791",
                "needs_improvement": false,
                "review_id": "fef6782e-3e57-4aaa-a503-e8b60ea51300",
                "section": "portfolio"
            },
            {
                "feedback": "The experience section is detailed and provides a good overview of your responsibilities and accomplishments. Use action verbs to start each bullet point. Quantify accomplishments whenever possible (e.g., \"Reduced server costs by X%...\").",
                "id": "693d57b8-9122-448d-bacd-1978e3a00c7b",
                "needs_improvement": false,
                "review_id": "fef6782e-3e57-4aaa-a503-e8b60ea51300",
                "section": "experience"
            },
            {
                "feedback": "The profile summary is a good start, but can be improved by quantifying achievements and being more specific about your contributions and the impact you've made. Highlight your key skills and tailor it to the specific job description you are applying for.",
                "id": "9dc1ef17-e068-43b3-92bd-448f4dd3f54c",
                "needs_improvement": true,
                "review_id": "fef6782e-3e57-4aaa-a503-e8b60ea51300",
                "section": "profile_summary"
            },
            {
                "feedback": "The education section is well-formatted and includes relevant coursework. The GPA is also a plus. Consider adding specific projects done during these courses if they are directly related to the jobs you're applying to.",
                "id": "fa7f14f2-b186-445d-b849-01c4286976f3",
                "needs_improvement": false,
                "review_id": "fef6782e-3e57-4aaa-a503-e8b60ea51300",
                "section": "education"
            }
        ],
        "submission": {
            "file_name": "my_cv.pdf",
            "file_type": "pdf",
            "file_url": "uploads\\5c3b3e3d-d116-4373-8a71-865ca19f409e.pdf",
            "id": "d351bde3-daec-41ee-8481-c75675be6be4",
            "uploaded_at": "2025-04-26T17:14:34",
            "user_id": "7faca6b6-8604-4d28-9d07-2ade7d70b4ae"
        }
    },
    ...
]
```

#### List Reviewed CV History API

---

- Method: ```GET```

- URL
```bash
{base}/api/v1/feature/cv/history/user/<user_id>
```

- Request URL
```bash
{base}/api/v1/feature/cv/history/user/7faca6b6-8604-4d28-9d07-2ade7d70b4ae
```

- Response:
```json
[
    {
        "file_name": "my_cv.pdf",
        "file_type": "pdf",
        "file_url": "uploads\\5c3b3e3d-d116-4373-8a71-865ca19f409e.pdf",
        "id": "d351bde3-daec-41ee-8481-c75675be6be4",
        "uploaded_at": "2025-04-26T17:14:34",
        "user_id": "7faca6b6-8604-4d28-9d07-2ade7d70b4ae"
    },
    ...
]
```

#### User Enroll Course API

---

- Method: ```POST```

- URL
```bash
{base}/api/v1/feature/courses/enroll
```

- Request Body:
```json
{
    "user_id": "5f684a9c-2bcb-4e40-b176-03277860a9f7",
    "course_id": "00bb8aa2-5b26-4cd3-b061-8f7a20eb94dc"
}
```

- Response:
```json
{
    "completed_at": null,
    "course_id": "00bb8aa2-5b26-4cd3-b061-8f7a20eb94dc",
    "enrolled_at": "2025-04-26T16:53:29",
    "id": "bdd17a8f-2a47-4904-a6f4-70b92e457dbc",
    "is_completed": false,
    "user_id": "5f684a9c-2bcb-4e40-b176-03277860a9f7"
}
```

#### Complete a Course API

---

- Method: ```POST```

- URL
```bash
{base}/api/v1/feature/courses/complete
```

- Request Body:
```json
{
    "user_id": "5f684a9c-2bcb-4e40-b176-03277860a9f7",
    "course_id": "00bb8aa2-5b26-4cd3-b061-8f7a20eb94dc"
}
```

- Response:
```json
{
    "completed_at": "2025-04-26T16:56:52",
    "course_id": "00bb8aa2-5b26-4cd3-b061-8f7a20eb94dc",
    "enrolled_at": "2025-04-26T16:53:29",
    "id": "bdd17a8f-2a47-4904-a6f4-70b92e457dbc",
    "is_completed": true,
    "user_id": "5f684a9c-2bcb-4e40-b176-03277860a9f7"
}
```

#### Unenroll a Course API

---

- Method: ```POST```

- URL
```bash
{base}/api/v1/feature/courses/unenroll
```

- Request Body:
```json
{
    "user_id": "5f684a9c-2bcb-4e40-b176-03277860a9f7",
    "course_id": "00bb8aa2-5b26-4cd3-b061-8f7a20eb94dc"
}
```

- Response:
```json
{
    "message": "Unenrolled successfully"
}
```

#### List History Enroll and Completed Course API

---

- Method: ```GET```

- URL
```bash
{base}/api/v1/feature/courses/user/<user_id>/enrollments
```

- Request URL
```bash
{base}/api/v1/feature/courses/user/5f684a9c-2bcb-4e40-b176-03277860a9f7/enrollments
```

- Response (Enrolled but Not Completed):
```json
[
    {
        "completed_at": null,
        "course_id": "00bb8aa2-5b26-4cd3-b061-8f7a20eb94dc",
        "enrolled_at": "2025-04-26T17:01:21",
        "id": "8803c851-59fa-4479-b989-7b61ed08ed19",
        "is_completed": false,
        "user_id": "5f684a9c-2bcb-4e40-b176-03277860a9f7"
    }
]
```

- Response (Enrolled but Completed):
```json
[
    {
        "completed_at": "2025-04-26T17:04:50",
        "course_id": "00bb8aa2-5b26-4cd3-b061-8f7a20eb94dc",
        "enrolled_at": "2025-04-26T17:01:21",
        "id": "8803c851-59fa-4479-b989-7b61ed08ed19",
        "is_completed": true,
        "user_id": "5f684a9c-2bcb-4e40-b176-03277860a9f7"
    }
]
```

#### List All Courses API

---

- Method: ```GET```

- URL
```bash
{base}/api/v1/feature/courses
```

- Response:
```json
[
    {
        "created_at": "2025-04-26T15:07:58",
        "description": "Description for C# Programming Fundamentals.",
        "id": "00bb8aa2-5b26-4cd3-b061-8f7a20eb94dc",
        "provider": "Udemy",
        "title": "C# Programming Fundamentals",
        "url": "https://example.com/c#-programming-fundamentals"
    },
    {
        "created_at": "2025-04-26T15:07:58",
        "description": "Description for Digital Marketing Essentials.",
        "id": "02710137-f971-41c7-b898-d6b98f07858f",
        "provider": "Udemy",
        "title": "Digital Marketing Essentials",
        "url": "https://example.com/digital-marketing-essentials"
    },
    {
        "created_at": "2025-04-26T15:07:58",
        "description": "Description for Network Administration Fundamentals.",
        "id": "0f3d9cbe-b91d-4a15-864e-51800ea2bee6",
        "provider": "Udemy",
        "title": "Network Administration Fundamentals",
        "url": "https://example.com/network-administration-fundamentals"
    },
    ...
]
```

#### Get a Specific Course Details API

---

- Method: ```GET```

- URL
```bash
{base}/api/v1/feature/courses/<string:course_id>
```

- URL
```bash
{base}/api/v1/feature/courses/00bb8aa2-5b26-4cd3-b061-8f7a20eb94dc
```

- Response:
```json
{
  "created_at": "2025-04-26T15:07:58",
  "description": "Description for C# Programming Fundamentals.",
  "id": "00bb8aa2-5b26-4cd3-b061-8f7a20eb94dc",
  "provider": "Udemy",
  "title": "C# Programming Fundamentals",
  "url": "https://example.com/c#-programming-fundamentals"
}
```

#### Create Profile Work Experience API

---

- Method: ```POST```

- URL
```bash
{base}/api/v1/users/<string:user_id>/work_experiences
```

- Request URL
```bash
{base}/api/v1/users/db604ac8-93cd-4d62-80a3-1f6900190bfa/work_experiences
```

- Request Body:
```json
{
    "job_title": "Senior Software Engineer",
    "company_name": "ExampleCorp",
    "job_desc": "Lead backend development and API design.",
    "start_month": 1,
    "start_year": 2020,
    "end_month": 12,
    "end_year": 2023,
    "is_current": false
}
```

- Response:
```json
{
    "company_name": "ExampleCorp",
    "created_at": "2025-04-27T06:34:12",
    "end_month": 12,
    "end_year": 2023,
    "id": "af9a0a88-66ee-4e79-b8da-e86a2e6ebdd4",
    "is_current": false,
    "job_desc": "Lead backend development and API design.",
    "job_title": "Senior Software Engineer",
    "start_month": 1,
    "start_year": 2020,
    "user_id": "db604ac8-93cd-4d62-80a3-1f6900190bfa"
}
```

#### Get All User Work Experience API

---

- Method: ```GET```

- URL
```bash
{base}/api/v1/users/<string:user_id>/work_experiences
```

- Request URL
```bash
{base}/api/v1/users/db604ac8-93cd-4d62-80a3-1f6900190bfa/work_experiences
```

- Response:
```json
[
    {
        "company_name": "ExampleCorp",
        "created_at": "2025-04-27T06:34:12",
        "end_month": 12,
        "end_year": 2023,
        "id": "af9a0a88-66ee-4e79-b8da-e86a2e6ebdd4",
        "is_current": false,
        "job_desc": "Lead backend development and API design.",
        "job_title": "Senior Software Engineer",
        "start_month": 1,
        "start_year": 2020,
        "user_id": "db604ac8-93cd-4d62-80a3-1f6900190bfa"
    },
    ...
]
```

#### Get Detail Experience API

---

- Method: ```GET```

- URL
```bash
{base}/api/v1/users/<user_id>/work_experiences/<exp_id>
```

- Request URL
```bash
{base}/api/v1/users/db604ac8-93cd-4d62-80a3-1f6900190bfa/work_experiences/af9a0a88-66ee-4e79-b8da-e86a2e6ebdd4
```

- Response:
```json
{
    "company_name": "ExampleCorp",
    "created_at": "2025-04-27T06:34:12",
    "end_month": 12,
    "end_year": 2023,
    "id": "af9a0a88-66ee-4e79-b8da-e86a2e6ebdd4",
    "is_current": false,
    "job_desc": "Lead backend development and API design.",
    "job_title": "Senior Software Engineer",
    "start_month": 1,
    "start_year": 2020,
    "user_id": "db604ac8-93cd-4d62-80a3-1f6900190bfa"
}
```

#### Update Detail Experience API

---

- Method: ```PUT```

- URL
```bash
{base}/api/v1/users/<user_id>/work_experiences/<exp_id>
```

- Request URL
```bash
{base}/api/v1/users/db604ac8-93cd-4d62-80a3-1f6900190bfa/work_experiences/af9a0a88-66ee-4e79-b8da-e86a2e6ebdd4
```

- Request Body:
```json
{
    "company_name": "ExampleCorp", (User Can Edit Freely)
    "created_at": "2025-04-27T06:34:12",
    "end_month": 12, (User Can Edit Freely)
    "end_year": 2023, (User Can Edit Freely)
    "id": "af9a0a88-66ee-4e79-b8da-e86a2e6ebdd4",
    "is_current": true, (User Can Edit Freely)
    "job_desc": "Architect scalable microservices.", (User Can Edit Freely)
    "job_title": "Senior Software Engineer", (User Can Edit Freely)
    "start_month": 1, (User Can Edit Freely)
    "start_year": 2020, (User Can Edit Freely)
    "user_id": "db604ac8-93cd-4d62-80a3-1f6900190bfa"
}
```
- Response:
```json
{
    "company_name": "ExampleCorp",
    "created_at": "2025-04-27T06:34:12",
    "end_month": 12,
    "end_year": 2023,
    "id": "af9a0a88-66ee-4e79-b8da-e86a2e6ebdd4",
    "is_current": true,
    "job_desc": "Architect scalable microservices.",
    "job_title": "Senior Software Engineer",
    "start_month": 1,
    "start_year": 2020,
    "user_id": "db604ac8-93cd-4d62-80a3-1f6900190bfa"
}
```
#### Delete Work Experience API

---

- Method: ```DELETE```

- URL
```bash
{base}/api/v1/users/<user_id>/work_experiences/<exp_id>
```

- Request URL
```bash
{base}/api/v1/users/db604ac8-93cd-4d62-80a3-1f6900190bfa/work_experiences/16a7dd27-fd0f-436a-9d5a-ea88a592b07c
```

#### Get All User Work Experience API

---

- Method: ```GET```

- URL
```bash
{base}/api/v1/jobs
```

- Response:
```json
[
    {
        "company": "SecureSys",
        "description": "Mobile Developer needed at SecureSys. You will be responsible for tasks related to mobile developer.",
        "id": "be83448f-fece-409b-a2ab-0e923b8cbd55",
        "location": "Yogyakarta, Indonesia",
        "posted_at": "2025-04-27T03:09:37",
        "requirements": "- Minimum 2 years experience as Mobile Developer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks",
        "title": "Mobile Developer"
    },
    {
        "company": "GlobalSoft",
        "description": "Quality Assurance Specialist needed at GlobalSoft. You will be responsible for tasks related to quality assurance specialist.",
        "id": "8e797fc1-5578-4ff5-a9f2-8315951e435d",
        "location": "Singapore",
        "posted_at": "2025-04-24T16:19:37",
        "requirements": "- Minimum 2 years experience as Quality Assurance Specialist\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks",
        "title": "Quality Assurance Specialist"
    },
    ...
]
```

#### Get All Job Roadmap API

---

- Method: ```GET```

- URL
```bash
{base}/api/v1/roadmaps
```

- Response:
```json
[
    {
        "description": "Key steps to start a career in cybersecurity analysis.",
        "id": "4a5ffc98-458b-4d7c-be77-ea0f345c0e33",
        "job_type": "Cybersecurity Analyst",
        "steps": [
            {
                "course_id": null,
                "description": "Learn OSI model, TCP/IP, and common network protocols.",
                "id": "eafe2fbd-2a8f-4038-843b-b3cd0f62a298",
                "step_order": 1,
                "title": "Networking Fundamentals"
            },
            {
                "course_id": null,
                "description": "Harden Linux systems and understand permissions.",
                "id": "3c2bdff8-d48b-45be-bae6-a7da65cc71ec",
                "step_order": 2,
                "title": "Linux Security Basics"
            },
            {
                "course_id": null,
                "description": "Study and practice preventing the OWASP Top 10 web flaws.",
                "id": "b9906303-a0e2-417b-93d5-59b608a16bd4",
                "step_order": 3,
                "title": "OWASP Top 10 Vulnerabilities"
            },
            {
                "course_id": null,
                "description": "Perform basic pentests using Metasploit Framework.",
                "id": "7be58ce9-56c1-4447-b8ce-affe6208c8df",
                "step_order": 4,
                "title": "Penetration Testing with Metasploit"
            },
            {
                "course_id": null,
                "description": "Set up log aggregation and alerts with a SIEM tool.",
                "id": "646c0bd1-cce3-48cb-ab19-d7cbb38dddff",
                "step_order": 5,
                "title": "Security Monitoring & SIEM"
            }
        ],
        "title": "Roadmap to Cybersecurity Analyst"
    },
    {
        "description": "Step-by-step learning plan to become a data scientist.",
        "id": "8399ffcb-dfef-4f5f-9bb7-168dceab4841",
        "job_type": "Data Scientist",
        "steps": [
            {
                "course_id": null,
                "description": "Cover NumPy, Pandas, and data manipulation basics.",
                "id": "4b49e0be-b6e0-4254-9867-c1fc93c691d3",
                "step_order": 1,
                "title": "Learn Python for Data Science"
            },
            {
                "course_id": null,
                "description": "Understand descriptive stats, distributions, and hypothesis testing.",
                "id": "e5cf6782-04ff-4485-b124-250b30bf0f0c",
                "step_order": 2,
                "title": "Statistics & Probability Basics"
            },
            {
                "course_id": null,
                "description": "Perform real-world data cleaning and exploratory analysis.",
                "id": "2358c538-a3e0-48af-9151-b488f8bdb7c1",
                "step_order": 3,
                "title": "Data Analysis with Pandas"
            },
            {
                "course_id": null,
                "description": "Learn supervised & unsupervised algorithms with scikit-learn.",
                "id": "55ea7c75-c618-41c7-baee-978454561b53",
                "step_order": 4,
                "title": "Machine Learning Fundamentals"
            },
            {
                "course_id": null,
                "description": "Wrap ML models into REST APIs using Flask or FastAPI.",
                "id": "5dcfd264-5d20-40c2-99c3-646a7c76479d",
                "step_order": 5,
                "title": "Model Deployment with Flask"
            }
        ],
        "title": "Roadmap to Data Scientist"
    },
   ...
]
```

#### Get a Roadmap Details API

---

- Method: ```GET```

- URL
```bash
{base}/api/v1/roadmaps/<rm_id>
```

- Request URL
```bash
{base}/api/v1/roadmaps/ead65b8c-7cd3-4266-91c3-a2e6d1e5dac3
```

- Response:
```json
{
    "description": "Your guide to mastering modern frontend development.",
    "id": "ead65b8c-7cd3-4266-91c3-a2e6d1e5dac3",
    "job_type": "Frontend Developer",
    "steps": [
        {
            "course_id": null, (Null/Dummy for Now - Admin must fill it manually | Next Update will integrated with the courses)
            "description": "Learn semantic HTML and responsive CSS layouts.",
            "id": "0f92bfa6-1799-4e5e-b394-64d3ea146ed1",
            "step_order": 1,
            "title": "HTML & CSS Fundamentals"
        },
        {
            "course_id": null,
            "description": "Understand modern JS syntax, promises, and async/await.",
            "id": "4c5aa5ca-6bab-459b-abdc-aa36f57ded21",
            "step_order": 2,
            "title": "JavaScript ES6+ Features"
        },
        {
            "course_id": null,
            "description": "Build component-based UIs with React and JSX.",
            "id": "528d17f5-e209-4f41-bb72-8d470e6554d8",
            "step_order": 3,
            "title": "React.js Basics"
        },
        {
            "course_id": null,
            "description": "Manage complex app state using Redux patterns.",
            "id": "29ef7677-16ae-468e-84b3-1d0b0b737121",
            "step_order": 4,
            "title": "State Management with Redux"
        },
        {
            "course_id": null,
            "description": "Write unit and integration tests for React components.",
            "id": "eb342862-542b-41c1-9312-62b667df8116",
            "step_order": 5,
            "title": "Frontend Testing with Jest"
        }
    ],
    "title": "Roadmap to Frontend Developer"
}
```

#### User Start/Choose a Roadmap API

---

- Method: ```POST```

- URL
```bash
{base}/api/v1/users/<string:user_id>/roadmaps/<string:rm_id>/start
```

- Request URL
```bash
{base}/api/v1/users/db604ac8-93cd-4d62-80a3-1f6900190bfa/roadmaps/ead65b8c-7cd3-4266-91c3-a2e6d1e5dac3/start
```

- Response:
```json
{
    "id": "d26c6073-7897-4372-bed4-e63a877afedf",
    "roadmap_id": "ead65b8c-7cd3-4266-91c3-a2e6d1e5dac3",
    "started_at": "2025-04-27T15:06:31",
    "user_id": "db604ac8-93cd-4d62-80a3-1f6900190bfa"
}
```

#### Get User List Took Roadmaps History API

---

- Method: ```GET```

- URL
```bash
{base}/api/v1/users/<string:user_id>/roadmaps
```

- Request URL
```bash
{base}/api/v1/users/db604ac8-93cd-4d62-80a3-1f6900190bfa/roadmaps
```

- Response:
```json
[
    {
        "id": "d26c6073-7897-4372-bed4-e63a877afedf",
        "roadmap": {
            "description": "Your guide to mastering modern frontend development.",
            "id": "ead65b8c-7cd3-4266-91c3-a2e6d1e5dac3",
            "job_type": "Frontend Developer",
            "steps": [
                {
                    "course_id": null,
                    "description": "Learn semantic HTML and responsive CSS layouts.",
                    "id": "0f92bfa6-1799-4e5e-b394-64d3ea146ed1",
                    "step_order": 1,
                    "title": "HTML & CSS Fundamentals"
                },
                {
                    "course_id": null,
                    "description": "Understand modern JS syntax, promises, and async/await.",
                    "id": "4c5aa5ca-6bab-459b-abdc-aa36f57ded21",
                    "step_order": 2,
                    "title": "JavaScript ES6+ Features"
                },
                {
                    "course_id": null,
                    "description": "Build component-based UIs with React and JSX.",
                    "id": "528d17f5-e209-4f41-bb72-8d470e6554d8",
                    "step_order": 3,
                    "title": "React.js Basics"
                },
                {
                    "course_id": null,
                    "description": "Manage complex app state using Redux patterns.",
                    "id": "29ef7677-16ae-468e-84b3-1d0b0b737121",
                    "step_order": 4,
                    "title": "State Management with Redux"
                },
                {
                    "course_id": null,
                    "description": "Write unit and integration tests for React components.",
                    "id": "eb342862-542b-41c1-9312-62b667df8116",
                    "step_order": 5,
                    "title": "Frontend Testing with Jest"
                }
            ],
            "title": "Roadmap to Frontend Developer"
        },
        "roadmap_id": "ead65b8c-7cd3-4266-91c3-a2e6d1e5dac3",
        "started_at": "2025-04-27T15:06:31",
        "user_id": "db604ac8-93cd-4d62-80a3-1f6900190bfa"
    }
]
```

#### User Complete a Step API

---

- Method: ```POST ```

- URL
```bash
{base}/api/v1/users/db604ac8-93cd-4d62-80a3-1f6900190bfa/roadmaps/ead65b8c-7cd3-4266-91c3-a2e6d1e5dac3/steps/0f92bfa6-1799-4e5e-b394-64d3ea146ed1/complete
```

- Request URL
```bash
{base}/api/v1/users/db604ac8-93cd-4d62-80a3-1f6900190bfa/roadmaps/ead65b8c-7cd3-4266-91c3-a2e6d1e5dac3/steps/0f92bfa6-1799-4e5e-b394-64d3ea146ed1/complete
```

- Response:
```json
{
    "completed_at": "2025-04-27T16:09:52",
    "step_id": "0f92bfa6-1799-4e5e-b394-64d3ea146ed1"
}
```


#### User Check Roadmap Progress API

---

- Method: ```GET```

- URL
```bash
{base}/api/v1/users/<string:user_id>/roadmaps/<string:roadmap_id>/progress
```

- Request URL
```bash
{base}/api/v1/users/db604ac8-93cd-4d62-80a3-1f6900190bfa/roadmaps/ead65b8c-7cd3-4266-91c3-a2e6d1e5dac3/progress
```

- Response:
```json
[
    {
        "completed": false, (Will change True if the user marked as complete)
        "completed_at": null,
        "course_id": null,
        "description": "Learn semantic HTML and responsive CSS layouts.",
        "id": "0f92bfa6-1799-4e5e-b394-64d3ea146ed1",
        "step_order": 1,
        "title": "HTML & CSS Fundamentals"
    },
    {
        "completed": false,
        "completed_at": null,
        "course_id": null,
        "description": "Understand modern JS syntax, promises, and async/await.",
        "id": "4c5aa5ca-6bab-459b-abdc-aa36f57ded21",
        "step_order": 2,
        "title": "JavaScript ES6+ Features"
    },
    {
        "completed": false,
        "completed_at": null,
        "course_id": null,
        "description": "Build component-based UIs with React and JSX.",
        "id": "528d17f5-e209-4f41-bb72-8d470e6554d8",
        "step_order": 3,
        "title": "React.js Basics"
    },
    {
        "completed": false,
        "completed_at": null,
        "course_id": null,
        "description": "Manage complex app state using Redux patterns.",
        "id": "29ef7677-16ae-468e-84b3-1d0b0b737121",
        "step_order": 4,
        "title": "State Management with Redux"
    },
    {
        "completed": false,
        "completed_at": null,
        "course_id": null,
        "description": "Write unit and integration tests for React components.",
        "id": "eb342862-542b-41c1-9312-62b667df8116",
        "step_order": 5,
        "title": "Frontend Testing with Jest"
    }
]
```
- Response (If Step is Marked Complete by User):
```json
[
    {
        "completed": true,
        "completed_at": "2025-04-27T16:09:52",
        "course_id": null,
        "description": "Learn semantic HTML and responsive CSS layouts.",
        "id": "0f92bfa6-1799-4e5e-b394-64d3ea146ed1",
        "step_order": 1,
        "title": "HTML & CSS Fundamentals"
    },
    ...
]
```

### Cloud Architecture

<div align="center">
  
![GCP-inTrain ai Architecture](https://github.com/user-attachments/assets/e59a98a6-a10a-4050-8c8c-700433b049b1)

</div>

### Deployment

- **Environment**: [Google Cloud Platform](https://cloud.google.com)
- **Server Deployments**: Cloud Run
- **Database Services**: Cloud SQL
- **Storage**: Cloud Storage

---

### License

<p align=justify>
There is <b>NO LICENSE</b> available yet as this project is still being used for purposes that cannot be published as open source, therefore please read the disclaimer section.
</p>

### Disclaimer

### Author

Github Organization: [inTrain.ai](https://github.com/intrain-ai)
