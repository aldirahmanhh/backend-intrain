-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 28, 2025 at 06:58 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `intrain`
--

-- --------------------------------------------------------

--
-- Table structure for table `achievements`
--

CREATE TABLE `achievements` (
  `id` char(36) NOT NULL,
  `user_id` char(36) NOT NULL,
  `roadmap_id` char(36) NOT NULL,
  `earned_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `chat_evaluations`
--

CREATE TABLE `chat_evaluations` (
  `id` char(36) NOT NULL,
  `session_id` char(36) NOT NULL,
  `score` tinyint(4) NOT NULL,
  `recommendations` text NOT NULL,
  `evaluated_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `chat_messages`
--

CREATE TABLE `chat_messages` (
  `id` char(36) NOT NULL,
  `session_id` char(36) NOT NULL,
  `sender` enum('user','bot') NOT NULL,
  `message` text NOT NULL,
  `sent_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `chat_sessions`
--

CREATE TABLE `chat_sessions` (
  `id` char(36) NOT NULL,
  `user_id` char(36) NOT NULL,
  `hr_level_id` int(11) NOT NULL,
  `job_type` varchar(200) NOT NULL,
  `total_questions` int(11) NOT NULL DEFAULT 0,
  `started_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `courses`
--

CREATE TABLE `courses` (
  `id` char(36) NOT NULL,
  `title` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `provider` varchar(100) DEFAULT NULL,
  `url` varchar(500) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `courses`
--

INSERT INTO `courses` (`id`, `title`, `description`, `provider`, `url`, `created_at`) VALUES
('072eb182-07ca-41e1-a40b-f5cc3a2f4360', 'Blockchain Basics', 'Description for Blockchain Basics.', 'Udemy', 'https://example.com/blockchain-basics', '2025-04-27 13:28:37'),
('07abfa23-51a0-4e6e-9480-852c22f42805', 'HTML & CSS Fundamentals', 'Learn semantic HTML5 and modern CSS layouts.', 'Udemy', 'https://example.com/html-css', '2025-06-28 11:56:17'),
('0b46be53-1298-4333-9706-efa3c607876b', 'AWS Certified Solutions Architect', 'Description for AWS Certified Solutions Architect.', 'Udemy', 'https://example.com/aws-certified-solutions-architect', '2025-04-27 13:28:37'),
('132547ce-92ec-492c-bc87-5080feb26ef4', 'Modern JavaScript ES6+', 'Deep dive into ES6+ features: modules, promises, async/await.', 'Udemy', 'https://example.com/js-es6', '2025-06-28 11:56:17'),
('15a6f412-c73a-4169-9738-806364e4dabf', 'Kubernetes Hands-On', 'Deploy, scale and manage containerized apps on Kubernetes.', 'Udemy', 'https://example.com/k8s-hands-on', '2025-06-28 11:56:17'),
('1a8f278f-e357-4104-8b04-80926c4cba0f', 'Ethical Hacking and Penetration Testing', 'Description for Ethical Hacking and Penetration Testing.', 'Udemy', 'https://example.com/ethical-hacking-and-penetration-testing', '2025-04-27 13:28:37'),
('1f1778b8-f96b-4fa7-8362-9b19ab82d435', 'Docker and Kubernetes Fundamentals', 'Description for Docker and Kubernetes Fundamentals.', 'Udemy', 'https://example.com/docker-and-kubernetes-fundamentals', '2025-04-27 13:28:37'),
('27187f76-b668-4237-a245-5e39dda6d884', 'Machine Learning A-Z™: Hands-On', 'Practical ML algorithms with scikit-learn and Python.', 'Udemy', 'https://example.com/ml-az', '2025-06-28 11:56:17'),
('2acd6e54-e8b1-4c25-b860-65879cb71e4f', 'DevOps with Jenkins and Terraform', 'Description for DevOps with Jenkins and Terraform.', 'Udemy', 'https://example.com/devops-with-jenkins-and-terraform', '2025-04-27 13:28:37'),
('3d6c0a3b-e9ae-43bc-ae39-47b1eb3e1f1a', 'Web Security Fundamentals', 'Description for Web Security Fundamentals.', 'Udemy', 'https://example.com/web-security-fundamentals', '2025-04-27 13:28:37'),
('3e691e6a-d53e-4dd8-ad53-876fafb89019', 'C# Programming Fundamentals', 'Description for C# Programming Fundamentals.', 'Udemy', 'https://example.com/c#-programming-fundamentals', '2025-04-27 13:28:37'),
('465454ec-a2ee-4d14-a8c3-cb23ea6aba85', 'Advanced Java Programming', 'Description for Advanced Java Programming.', 'Udemy', 'https://example.com/advanced-java-programming', '2025-04-27 13:28:37'),
('536938c3-ffee-4001-a515-0f64a36bc79a', 'Graphic Design with Photoshop', 'Description for Graphic Design with Photoshop.', 'Udemy', 'https://example.com/graphic-design-with-photoshop', '2025-04-27 13:28:37'),
('538943a7-6800-4ed6-95f5-c72486ff6981', 'Redux for State Management', 'Manage complex application state with Redux patterns.', 'Udemy', 'https://example.com/redux-patterns', '2025-06-28 11:56:17'),
('5a745adf-6a69-4143-af10-85226173e6f8', 'Docker Mastery', 'Containerize applications and write Dockerfile best practices.', 'Udemy', 'https://example.com/docker-mastery', '2025-06-28 11:56:17'),
('65210dc7-a73b-4a14-b3a0-18ea5d10d872', 'Introduction to Java', 'Description for Introduction to Java.', 'Udemy', 'https://example.com/introduction-to-java', '2025-04-27 13:28:37'),
('6ac62a35-aec7-459b-abe0-e33a199923b6', 'CI/CD with GitHub Actions', 'Automate builds, tests and deployments with GitHub Actions.', 'Udemy', 'https://example.com/github-actions', '2025-06-28 11:56:17'),
('742aba42-c415-43b7-872e-0002d8f80736', 'Statistics & Probability for Data Science', 'Foundations of statistics, distributions, hypothesis testing.', 'Coursera', 'https://example.com/stats-ds', '2025-06-28 11:56:17'),
('84cdcbda-53e5-44ed-b3ca-57a97964687b', 'Network Administration Fundamentals', 'Description for Network Administration Fundamentals.', 'Udemy', 'https://example.com/network-administration-fundamentals', '2025-04-27 13:28:37'),
('8a8c64fb-d2bf-4962-be4f-3a289db93989', 'Business Analytics with Power BI', 'Description for Business Analytics with Power BI.', 'Udemy', 'https://example.com/business-analytics-with-power-bi', '2025-04-27 13:28:37'),
('98059442-a2ff-48b8-862b-d3ae7729dbab', 'NoSQL Database Design', 'Description for NoSQL Database Design.', 'Udemy', 'https://example.com/nosql-database-design', '2025-04-27 13:28:37'),
('a252bc63-f180-4bf8-aef1-fe3e52e934ec', 'Android App Development with Kotlin', 'Description for Android App Development with Kotlin.', 'Udemy', 'https://example.com/android-app-development-with-kotlin', '2025-04-27 13:28:37'),
('a5f15689-3fbc-4195-a07d-5b6ed95e3f96', 'REST APIs with Flask', 'Build and deploy RESTful services using Flask and Python.', 'Udemy', 'https://example.com/flask-apis', '2025-06-28 11:56:17'),
('a84ccbd2-3ad3-4ba9-b9b6-40f6457eaf86', 'Cybersecurity for Beginners', 'Description for Cybersecurity for Beginners.', 'Udemy', 'https://example.com/cybersecurity-for-beginners', '2025-04-27 13:28:37'),
('b13ba382-eecb-4950-a114-8026a9d37723', 'SEO and SEM Strategies', 'Description for SEO and SEM Strategies.', 'Udemy', 'https://example.com/seo-and-sem-strategies', '2025-04-27 13:28:37'),
('b70144e6-aca8-4df8-a57e-8ac8b8698feb', 'Terraform: Infrastructure as Code', 'Provision and manage infrastructure with Terraform.', 'Udemy', 'https://example.com/terraform-iac', '2025-06-28 11:56:17'),
('bcd50e42-6173-424c-9d95-89f18c0454b0', 'Digital Marketing Essentials', 'Description for Digital Marketing Essentials.', 'Udemy', 'https://example.com/digital-marketing-essentials', '2025-04-27 13:28:37'),
('e013b7b2-fc08-4a79-9cb6-53d2d7646b48', 'Linux System Administration', 'Description for Linux System Administration.', 'Udemy', 'https://example.com/linux-system-administration', '2025-04-27 13:28:37'),
('e03e4906-f7b7-49dc-9525-47c4eb58f78b', 'Mobile App Development with Flutter', 'Description for Mobile App Development with Flutter.', 'Udemy', 'https://example.com/mobile-app-development-with-flutter', '2025-04-27 13:28:37'),
('e2fef3fa-03a7-492d-9273-d552adc1e20e', 'Testing React with Jest', 'Write unit and integration tests for React components using Jest.', 'Udemy', 'https://example.com/jest-react', '2025-06-28 11:56:17'),
('e35a8bc2-378c-4c4e-a8fa-73f653336f86', 'Cloud Computing Basics', 'Description for Cloud Computing Basics.', 'Udemy', 'https://example.com/cloud-computing-basics', '2025-04-27 13:28:37'),
('e4a36b86-8e72-430e-95b9-099eba63786b', '.NET Core Development', 'Description for .NET Core Development.', 'Udemy', 'https://example.com/.net-core-development', '2025-04-27 13:28:37'),
('e53e8ea6-2859-4acc-85a8-99ea6b34e43e', 'Metasploit for Pentesters', 'Learn pentesting with Metasploit Framework.', 'Udemy', 'https://example.com/metasploit', '2025-06-28 11:56:17'),
('e6113de0-feb5-4248-a31c-8b177f65f173', 'Data Structures & Algorithms in Python', 'Deep dive on arrays, linked lists, trees, graphs, sorting and searching in Python.', 'Udemy', 'https://example.com/dsa-python', '2025-06-28 11:56:17'),
('e8885aea-f10f-40fb-93d2-287fccd54486', 'OWASP Top 10 Hands-On', 'Practical exercises for the OWASP Top 10 web vulnerabilities.', 'Udemy', 'https://example.com/owasp-top10', '2025-06-28 11:56:17'),
('f10d3ad8-13ac-48de-b762-8ebbf740a6ac', 'iOS App Development with Swift', 'Description for iOS App Development with Swift.', 'Udemy', 'https://example.com/ios-app-development-with-swift', '2025-04-27 13:28:37'),
('f2250f31-bc44-4987-a539-47e67debd778', 'Introduction to SQL and Databases', 'Description for Introduction to SQL and Databases.', 'Udemy', 'https://example.com/introduction-to-sql-and-databases', '2025-04-27 13:28:37'),
('f27739f8-f621-4c10-b659-54afd26101e0', 'UI/UX Design Principles', 'Description for UI/UX Design Principles.', 'Udemy', 'https://example.com/ui/ux-design-principles', '2025-04-27 13:28:37'),
('f311b2f5-a539-45e1-9127-954148a4864d', 'React.js Basics', 'Build component-based UIs with React and JSX.', 'Udemy', 'https://example.com/react-basics', '2025-06-28 11:56:17'),
('fd04598f-e347-49a0-8c57-93500853eb3f', 'Data Analysis with Excel', 'Description for Data Analysis with Excel.', 'Udemy', 'https://example.com/data-analysis-with-excel', '2025-04-27 13:28:37');

-- --------------------------------------------------------

--
-- Table structure for table `course_enrollments`
--

CREATE TABLE `course_enrollments` (
  `id` char(36) NOT NULL,
  `user_id` char(36) NOT NULL,
  `course_id` char(36) NOT NULL,
  `enrolled_at` datetime NOT NULL DEFAULT current_timestamp(),
  `is_completed` tinyint(1) NOT NULL DEFAULT 0,
  `completed_at` datetime DEFAULT NULL,
  `enrolled_status` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `cv_reviews`
--

CREATE TABLE `cv_reviews` (
  `id` char(36) NOT NULL,
  `submission_id` char(36) NOT NULL,
  `reviewed_at` datetime DEFAULT current_timestamp(),
  `ats_passed` tinyint(1) NOT NULL,
  `overall_feedback` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `cv_review_sections`
--

CREATE TABLE `cv_review_sections` (
  `id` char(36) NOT NULL,
  `review_id` char(36) NOT NULL,
  `section` enum('profile_summary','education','experience','skills','certification','portfolio') NOT NULL,
  `needs_improvement` tinyint(1) NOT NULL,
  `feedback` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `cv_submissions`
--

CREATE TABLE `cv_submissions` (
  `id` char(36) NOT NULL,
  `user_id` char(36) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `file_type` enum('pdf','jpg','jpeg','png') NOT NULL,
  `file_url` varchar(500) NOT NULL,
  `uploaded_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `hr_levels`
--

CREATE TABLE `hr_levels` (
  `id` int(11) NOT NULL,
  `name` varchar(20) NOT NULL,
  `description` varchar(100) DEFAULT NULL,
  `difficulty_rank` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `hr_levels`
--

INSERT INTO `hr_levels` (`id`, `name`, `description`, `difficulty_rank`) VALUES
(1, 'Easy', 'A beginner friendly, very supportive and calming HR', 1),
(2, 'Normal', 'Need a bit of professional experiences, a Tough one', 2),
(3, 'Hard', 'Highly experienced HR and very sarcastic, a little hurtful', 3);

-- --------------------------------------------------------

--
-- Table structure for table `jobs`
--

CREATE TABLE `jobs` (
  `id` char(36) NOT NULL,
  `title` varchar(200) NOT NULL,
  `company` varchar(100) DEFAULT NULL,
  `location` varchar(100) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `requirements` text DEFAULT NULL,
  `posted_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `jobs`
--

INSERT INTO `jobs` (`id`, `title`, `company`, `location`, `description`, `requirements`, `posted_at`) VALUES
('044f1779-41c8-46c2-886b-7d7e1907aabe', 'Cloud Architect', 'GlobalSoft', 'Singapore', 'Cloud Architect needed at GlobalSoft. You will be responsible for tasks related to cloud architect.', '- Minimum 2 years experience as Cloud Architect\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-11 01:08:37'),
('0885f6fc-e67a-45ef-af93-200fdc22d262', 'Financial Analyst', 'SecureSys', 'Yogyakarta, Indonesia', 'Financial Analyst needed at SecureSys. You will be responsible for tasks related to financial analyst.', '- Minimum 2 years experience as Financial Analyst\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-16 12:18:37'),
('0aec099e-886b-4cb0-b332-cf3f85b385cf', 'Financial Analyst', 'NextGen Labs', 'Bandung, Indonesia', 'Financial Analyst needed at NextGen Labs. You will be responsible for tasks related to financial analyst.', '- Minimum 2 years experience as Financial Analyst\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-01 17:09:37'),
('14c67ca8-0597-411f-9c27-442f0a3b5b16', 'QA Engineer', 'YourCompany', 'Jakarta, Indonesia', 'QA Engineer role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('19fcc6d1-597e-471c-8fb0-30f317df57a7', 'Frontend Developer', 'YourCompany', 'Jakarta, Indonesia', 'Frontend Developer role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('1f5f372b-6951-406d-8b7c-5dbad1586417', 'Full Stack Developer', 'YourCompany', 'Jakarta, Indonesia', 'Full Stack Developer role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('20c595d5-697f-403e-895d-56625d9c13b0', 'Customer Support Representative', 'Innova Solutions', 'Tokyo, Japan', 'Customer Support Representative needed at Innova Solutions. You will be responsible for tasks related to customer support representative.', '- Minimum 2 years experience as Customer Support Representative\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-15 10:47:37'),
('214ebbc0-03c2-4f0c-b8e4-d5066ef5c910', 'Software Engineer', 'CloudNine', 'Yogyakarta, Indonesia', 'Software Engineer needed at CloudNine. You will be responsible for tasks related to software engineer.', '- Minimum 2 years experience as Software Engineer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-03-29 16:49:37'),
('26a08062-281d-4f18-ab43-2191c4e513b7', 'Network Engineer', 'CloudNine', 'Yogyakarta, Indonesia', 'Network Engineer needed at CloudNine. You will be responsible for tasks related to network engineer.', '- Minimum 2 years experience as Network Engineer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-09 21:22:37'),
('2b21848b-89cd-4f56-82c7-22674c12d4b4', 'Software Engineer', 'DataDrive', 'Surabaya, Indonesia', 'Software Engineer needed at DataDrive. You will be responsible for tasks related to software engineer.', '- Minimum 2 years experience as Software Engineer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-03-28 03:38:37'),
('2dbdd43f-2c6d-4ab4-86b2-97e65a00a7b0', 'Software Engineer', 'VisionTech', 'Jakarta, Indonesia', 'Software Engineer needed at VisionTech. You will be responsible for tasks related to software engineer.', '- Minimum 2 years experience as Software Engineer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-22 13:39:37'),
('2e4cdd9f-5ce2-406a-abbd-f2f0a9f7ecfa', 'Event Planner', 'NextGen Labs', 'Jakarta, Indonesia', 'Event Planner needed at NextGen Labs. You will be responsible for tasks related to event planner.', '- Minimum 2 years experience as Event Planner\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-07 14:29:37'),
('2fd56c62-66e5-4d20-b3ad-af8e279bc9ff', 'Network Engineer', 'DataDrive', 'Bandung, Indonesia', 'Network Engineer needed at DataDrive. You will be responsible for tasks related to network engineer.', '- Minimum 2 years experience as Network Engineer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-10 19:10:37'),
('33a614d2-b446-4f47-9d18-815b21c6b47d', 'System Administrator', 'GlobalSoft', 'London, UK', 'System Administrator needed at GlobalSoft. You will be responsible for tasks related to system administrator.', '- Minimum 2 years experience as System Administrator\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-08 01:39:37'),
('33fa83e9-24a7-4bf1-9381-cb00c97d784c', 'Data Scientist', 'YourCompany', 'Jakarta, Indonesia', 'Data Scientist role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('34603b16-ca95-472d-ba55-cdd380f05faf', 'Procurement Officer', 'CloudNine', 'Yogyakarta, Indonesia', 'Procurement Officer needed at CloudNine. You will be responsible for tasks related to procurement officer.', '- Minimum 2 years experience as Procurement Officer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-09 09:49:37'),
('349c70e9-5e5b-4d1c-a249-3f6d8bc36149', 'Security Analyst', 'YourCompany', 'Jakarta, Indonesia', 'Security Analyst role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('360a0202-10a4-460e-aca3-e3fe81ba31b6', 'System Administrator', 'YourCompany', 'Jakarta, Indonesia', 'System Administrator role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('36ae3a28-86d3-417d-922c-8ea18c1aedb5', 'Database Administrator', 'YourCompany', 'Jakarta, Indonesia', 'Database Administrator role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('3e78a8a2-6195-464b-90c1-f3eed379701a', 'System Administrator', 'SecureSys', 'New York, USA', 'System Administrator needed at SecureSys. You will be responsible for tasks related to system administrator.', '- Minimum 2 years experience as System Administrator\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-23 01:40:37'),
('41159a71-2acd-4cfb-9cc6-6a1f43778a82', 'QA Engineer', 'AppWorks', 'London, UK', 'QA Engineer needed at AppWorks. You will be responsible for tasks related to qa engineer.', '- Minimum 2 years experience as QA Engineer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-19 00:13:37'),
('44025619-3152-4fc6-8ba7-f94d9451cf5e', 'HR Specialist', 'NextGen Labs', 'Singapore', 'HR Specialist needed at NextGen Labs. You will be responsible for tasks related to hr specialist.', '- Minimum 2 years experience as HR Specialist\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-15 05:58:37'),
('52135c43-8672-484e-9075-70e0b1150922', 'Mobile Developer', 'YourCompany', 'Jakarta, Indonesia', 'Mobile Developer role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('5885a944-5c9d-418d-8223-9b530f59cac1', 'Full Stack Developer', 'SecureSys', 'Seoul, South Korea', 'Full Stack Developer needed at SecureSys. You will be responsible for tasks related to full stack developer.', '- Minimum 2 years experience as Full Stack Developer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-16 17:16:37'),
('59b9297a-4d31-4039-86e0-778243124ac1', 'DevOps Engineer', 'YourCompany', 'Jakarta, Indonesia', 'DevOps Engineer role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('5ca22141-95af-4592-a7ce-58b626bcac7b', 'Mobile Developer', 'DataDrive', 'New York, USA', 'Mobile Developer needed at DataDrive. You will be responsible for tasks related to mobile developer.', '- Minimum 2 years experience as Mobile Developer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-09 13:46:37'),
('5d2545a9-b985-4a13-b72a-013c130c0582', 'Business Analyst', 'YourCompany', 'Jakarta, Indonesia', 'Business Analyst role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('5ef7d10d-b59d-4419-80ee-413dcd4ca553', 'Data Scientist', 'AppWorks', 'Yogyakarta, Indonesia', 'Data Scientist needed at AppWorks. You will be responsible for tasks related to data scientist.', '- Minimum 2 years experience as Data Scientist\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-18 11:28:37'),
('612e1040-0171-4691-b237-a74627d05ca3', 'QA Engineer', 'TechCorp', 'New York, USA', 'QA Engineer needed at TechCorp. You will be responsible for tasks related to qa engineer.', '- Minimum 2 years experience as QA Engineer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-03-29 20:15:37'),
('64bc9704-e4b3-4d4a-bc94-51a1ce9c5fd6', 'Network Engineer', 'GlobalSoft', 'Yogyakarta, Indonesia', 'Network Engineer needed at GlobalSoft. You will be responsible for tasks related to network engineer.', '- Minimum 2 years experience as Network Engineer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-03-31 14:15:37'),
('68ca0283-ada7-4bf4-ad4a-6827d9ac2166', 'Data Scientist', 'VisionTech', 'London, UK', 'Data Scientist needed at VisionTech. You will be responsible for tasks related to data scientist.', '- Minimum 2 years experience as Data Scientist\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-07 00:05:37'),
('69d51dfa-7115-47ab-8ef1-3956b158fff4', 'Content Writer', 'AppWorks', 'Seoul, South Korea', 'Content Writer needed at AppWorks. You will be responsible for tasks related to content writer.', '- Minimum 2 years experience as Content Writer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-21 16:22:37'),
('6b75fdc7-20d1-4c1a-9ee0-31b8bf82b731', 'Financial Analyst', 'YourCompany', 'Jakarta, Indonesia', 'Financial Analyst role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('6c8455ba-f472-479e-a04b-b6bd1543ce4c', 'Network Engineer', 'YourCompany', 'Jakarta, Indonesia', 'Network Engineer role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('6cadb49c-0f04-42c6-b317-d0466fb58774', 'Sales Executive', 'YourCompany', 'Jakarta, Indonesia', 'Sales Executive role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('6ed0290a-a67d-467c-ace2-c79cd3084709', 'Customer Support Representative', 'YourCompany', 'Jakarta, Indonesia', 'Customer Support Representative role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('700059d0-f40c-4849-96f7-efe572315d3e', 'Full Stack Developer', 'NextGen Labs', 'Tokyo, Japan', 'Full Stack Developer needed at NextGen Labs. You will be responsible for tasks related to full stack developer.', '- Minimum 2 years experience as Full Stack Developer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-10 02:23:37'),
('7a55048b-1514-4006-a70e-52c901ab8a27', 'Financial Analyst', 'DataDrive', 'Jakarta, Indonesia', 'Financial Analyst needed at DataDrive. You will be responsible for tasks related to financial analyst.', '- Minimum 2 years experience as Financial Analyst\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-17 13:50:37'),
('7e9f8f12-6483-401c-8e26-d7e4c6fd9db0', 'Data Scientist', 'DataDrive', 'Bali, Indonesia', 'Data Scientist needed at DataDrive. You will be responsible for tasks related to data scientist.', '- Minimum 2 years experience as Data Scientist\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-16 22:54:37'),
('82f98e58-c0d9-40cb-bb54-f4d74dbdc860', 'Logistics Coordinator', 'YourCompany', 'Jakarta, Indonesia', 'Logistics Coordinator role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('83863d0d-8727-4370-9def-1772fed525a3', 'Software Engineer', 'YourCompany', 'Jakarta, Indonesia', 'Software Engineer role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('865aca86-633f-42cf-bf58-8d17b94ee13c', 'Content Writer', 'SecureSys', 'Singapore', 'Content Writer needed at SecureSys. You will be responsible for tasks related to content writer.', '- Minimum 2 years experience as Content Writer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-03-27 13:23:37'),
('8e6881b4-0916-4764-b03b-3bef06e0b8d5', 'Logistics Coordinator', 'Webify', 'Jakarta, Indonesia', 'Logistics Coordinator needed at Webify. You will be responsible for tasks related to logistics coordinator.', '- Minimum 2 years experience as Logistics Coordinator\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-20 05:51:37'),
('8e797fc1-5578-4ff5-a9f2-8315951e435d', 'Quality Assurance Specialist', 'GlobalSoft', 'Singapore', 'Quality Assurance Specialist needed at GlobalSoft. You will be responsible for tasks related to quality assurance specialist.', '- Minimum 2 years experience as Quality Assurance Specialist\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-24 16:19:37'),
('93aad476-9550-496f-9555-5d946722b9b5', 'Operations Manager', 'VisionTech', 'London, UK', 'Operations Manager needed at VisionTech. You will be responsible for tasks related to operations manager.', '- Minimum 2 years experience as Operations Manager\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-04 19:54:37'),
('9a09047c-7826-4a35-91d7-1f3b2074d327', 'HR Specialist', 'Innova Solutions', 'Singapore', 'HR Specialist needed at Innova Solutions. You will be responsible for tasks related to hr specialist.', '- Minimum 2 years experience as HR Specialist\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-03-30 18:38:37'),
('a18ad839-2c9a-49ad-84df-c9f1716df271', 'Software Engineer', 'NextGen Labs', 'New York, USA', 'Software Engineer needed at NextGen Labs. You will be responsible for tasks related to software engineer.', '- Minimum 2 years experience as Software Engineer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-23 19:18:37'),
('a98fd3ff-eaa9-4fac-8bef-98957cb08c13', 'Financial Analyst', 'TechCorp', 'Surabaya, Indonesia', 'Financial Analyst needed at TechCorp. You will be responsible for tasks related to financial analyst.', '- Minimum 2 years experience as Financial Analyst\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-18 12:33:37'),
('a9b29434-c165-409e-8d1f-edfc2e2642fc', 'Financial Analyst', 'DataDrive', 'New York, USA', 'Financial Analyst needed at DataDrive. You will be responsible for tasks related to financial analyst.', '- Minimum 2 years experience as Financial Analyst\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-03-29 08:41:37'),
('aa15a543-6c4d-45db-9c7a-591dfe9139c0', 'Frontend Developer', 'TechCorp', 'Seoul, South Korea', 'Frontend Developer needed at TechCorp. You will be responsible for tasks related to frontend developer.', '- Minimum 2 years experience as Frontend Developer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-10 15:08:37'),
('b1cad227-ab90-4f51-9f83-16ce75392837', 'Product Manager', 'YourCompany', 'Jakarta, Indonesia', 'Product Manager role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('b2ec0c16-8dc3-4fbd-b01b-9e42ce2c3baa', 'Logistics Coordinator', 'NextGen Labs', 'London, UK', 'Logistics Coordinator needed at NextGen Labs. You will be responsible for tasks related to logistics coordinator.', '- Minimum 2 years experience as Logistics Coordinator\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-01 00:33:37'),
('bbff996a-d964-47ff-a719-e46f51bfb0d4', 'Operations Manager', 'YourCompany', 'Jakarta, Indonesia', 'Operations Manager role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('be38192f-845d-4c96-9af5-b81209316a6f', 'Security Analyst', 'NextGen Labs', 'Jakarta, Indonesia', 'Security Analyst needed at NextGen Labs. You will be responsible for tasks related to security analyst.', '- Minimum 2 years experience as Security Analyst\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-20 19:00:37'),
('be83448f-fece-409b-a2ab-0e923b8cbd55', 'Mobile Developer', 'SecureSys', 'Yogyakarta, Indonesia', 'Mobile Developer needed at SecureSys. You will be responsible for tasks related to mobile developer.', '- Minimum 2 years experience as Mobile Developer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-27 03:09:37'),
('c21636c8-1f10-4f88-91fe-70891e6f0e78', 'DevOps Engineer', 'TechCorp', 'Seoul, South Korea', 'DevOps Engineer needed at TechCorp. You will be responsible for tasks related to devops engineer.', '- Minimum 2 years experience as DevOps Engineer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-12 18:04:37'),
('c35037b9-aa6c-435a-81fd-2c6f84812fbf', 'Customer Support Representative', 'GlobalSoft', 'Bali, Indonesia', 'Customer Support Representative needed at GlobalSoft. You will be responsible for tasks related to customer support representative.', '- Minimum 2 years experience as Customer Support Representative\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-08 03:15:37'),
('c93abb35-b70d-4057-905a-7c8084bd07b7', 'Cloud Architect', 'YourCompany', 'Jakarta, Indonesia', 'Cloud Architect role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('cdbced31-93df-4cc1-8885-51b1bb231a2d', 'QA Engineer', 'Webify', 'Yogyakarta, Indonesia', 'QA Engineer needed at Webify. You will be responsible for tasks related to qa engineer.', '- Minimum 2 years experience as QA Engineer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-03 09:10:37'),
('cdebac03-c963-4b63-a8ca-f668912a5d02', 'Data Scientist', 'GlobalSoft', 'Tokyo, Japan', 'Data Scientist needed at GlobalSoft. You will be responsible for tasks related to data scientist.', '- Minimum 2 years experience as Data Scientist\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-09 23:36:37'),
('ce6041b4-caa5-4ce1-ba47-82f4f8753814', 'System Administrator', 'VisionTech', 'Surabaya, Indonesia', 'System Administrator needed at VisionTech. You will be responsible for tasks related to system administrator.', '- Minimum 2 years experience as System Administrator\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-08 18:56:37'),
('d340f81d-a57a-4c7f-a3f4-1629ca6858be', 'HR Specialist', 'YourCompany', 'Jakarta, Indonesia', 'HR Specialist role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('d5ae1ba3-261b-42f2-b8bb-00bec7222035', 'Operations Manager', 'Innova Solutions', 'Tokyo, Japan', 'Operations Manager needed at Innova Solutions. You will be responsible for tasks related to operations manager.', '- Minimum 2 years experience as Operations Manager\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-18 01:56:37'),
('d826cc41-bab2-4cd5-95cf-c01156785630', 'Software Engineer', 'AppWorks', 'Bandung, Indonesia', 'Software Engineer needed at AppWorks. You will be responsible for tasks related to software engineer.', '- Minimum 2 years experience as Software Engineer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-01 02:21:37'),
('de79609e-e1bc-44b3-8d27-df4d173a3d15', 'Sales Executive', 'NextGen Labs', 'Tokyo, Japan', 'Sales Executive needed at NextGen Labs. You will be responsible for tasks related to sales executive.', '- Minimum 2 years experience as Sales Executive\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-03-30 08:23:37'),
('e14d4fb4-f176-4f08-8550-391daf7389ae', 'Software Engineer', 'VisionTech', 'London, UK', 'Software Engineer needed at VisionTech. You will be responsible for tasks related to software engineer.', '- Minimum 2 years experience as Software Engineer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-18 19:26:37'),
('e314f070-3498-4af8-a992-8e0f71714d92', 'Backend Developer', 'YourCompany', 'Jakarta, Indonesia', 'Backend Developer role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('e5800735-2cc9-42a1-8672-84d69faf98b1', 'UX Designer', 'YourCompany', 'Jakarta, Indonesia', 'UX Designer role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('e603361c-997e-4761-b43d-5100642d6c0b', 'UX Designer', 'Innova Solutions', 'Yogyakarta, Indonesia', 'UX Designer needed at Innova Solutions. You will be responsible for tasks related to ux designer.', '- Minimum 2 years experience as UX Designer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-22 21:34:37'),
('e7079799-757b-40d2-9312-e1942bec8ef5', 'Graphic Designer', 'VisionTech', 'Singapore', 'Graphic Designer needed at VisionTech. You will be responsible for tasks related to graphic designer.', '- Minimum 2 years experience as Graphic Designer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-09 13:33:37'),
('e9a6f31d-4e92-4e32-bcf2-b703d1155874', 'Social Media Manager', 'YourCompany', 'Jakarta, Indonesia', 'Social Media Manager role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('ebe46602-ae96-4feb-a2de-4f7ec44bf5ef', 'Backend Developer', 'Webify', 'New York, USA', 'Backend Developer needed at Webify. You will be responsible for tasks related to backend developer.', '- Minimum 2 years experience as Backend Developer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-15 16:03:37'),
('ed63adc2-a283-4f29-ae11-aad1a2e878f4', 'Marketing Manager', 'YourCompany', 'Jakarta, Indonesia', 'Marketing Manager role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('f37eeb1f-a79b-453a-a890-e76b67784f1d', 'Content Writer', 'YourCompany', 'Jakarta, Indonesia', 'Content Writer role at YourCompany. Detailed role description goes here.', '- Relevant experience\n- Strong communication skills\n- Team player attitude', '2025-04-27 20:34:34'),
('fc5dd499-b591-4baa-9328-e27597b9000d', 'UX Designer', 'Webify', 'Surabaya, Indonesia', 'UX Designer needed at Webify. You will be responsible for tasks related to ux designer.', '- Minimum 2 years experience as UX Designer\n- Good communication skills\n- Team player\n- Familiar with relevant tools and frameworks', '2025-04-14 22:53:37');

-- --------------------------------------------------------

--
-- Table structure for table `mentorship_feedback`
--

CREATE TABLE `mentorship_feedback` (
  `id` char(36) NOT NULL,
  `session_id` char(36) NOT NULL,
  `rating` int(11) NOT NULL,
  `feedback` text DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `mentorship_sessions`
--

CREATE TABLE `mentorship_sessions` (
  `id` char(36) NOT NULL,
  `mentee_id` char(36) NOT NULL,
  `mentor_id` char(36) NOT NULL,
  `scheduled_at` datetime NOT NULL,
  `meet_link` varchar(300) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `completed` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `mentor_availabilities`
--

CREATE TABLE `mentor_availabilities` (
  `id` char(36) NOT NULL,
  `mentor_id` char(36) NOT NULL,
  `start_datetime` datetime NOT NULL,
  `end_datetime` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `mentor_profiles`
--

CREATE TABLE `mentor_profiles` (
  `id` char(36) NOT NULL,
  `user_id` char(36) NOT NULL,
  `expertise` varchar(200) NOT NULL,
  `bio` text DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `roadmaps`
--

CREATE TABLE `roadmaps` (
  `id` char(36) NOT NULL,
  `job_type` varchar(200) NOT NULL,
  `title` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `roadmaps`
--

INSERT INTO `roadmaps` (`id`, `job_type`, `title`, `description`, `created_at`) VALUES
('1ff976d2-b5af-4585-9baf-f3f9bff3869c', 'Software Engineer', 'Roadmap to Software Engineer', 'A focused path to master core software engineering skills.', '2025-04-27 21:58:59'),
('4a5ffc98-458b-4d7c-be77-ea0f345c0e33', 'Cybersecurity Analyst', 'Roadmap to Cybersecurity Analyst', 'Key steps to start a career in cybersecurity analysis.', '2025-04-27 21:58:59'),
('8399ffcb-dfef-4f5f-9bb7-168dceab4841', 'Data Scientist', 'Roadmap to Data Scientist', 'Step-by-step learning plan to become a data scientist.', '2025-04-27 21:58:59'),
('d0d0ed3e-a250-48a9-9cc8-9bf067231a21', 'DevOps Engineer', 'Roadmap to DevOps Engineer', 'Essential DevOps skills from development to production.', '2025-04-27 21:58:59'),
('ead65b8c-7cd3-4266-91c3-a2e6d1e5dac3', 'Frontend Developer', 'Roadmap to Frontend Developer', 'Your guide to mastering modern frontend development.', '2025-04-27 21:58:59');

-- --------------------------------------------------------

--
-- Table structure for table `roadmap_steps`
--

CREATE TABLE `roadmap_steps` (
  `id` char(36) NOT NULL,
  `roadmap_id` char(36) NOT NULL,
  `step_order` int(11) NOT NULL,
  `title` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `course_id` char(36) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `roadmap_steps`
--

INSERT INTO `roadmap_steps` (`id`, `roadmap_id`, `step_order`, `title`, `description`, `course_id`, `created_at`) VALUES
('00e412f2-f0d0-4a8e-9e81-dd1324316afa', 'd0d0ed3e-a250-48a9-9cc8-9bf067231a21', 4, 'CI/CD with Jenkins', 'Build automated pipelines for test, build, and deploy.', NULL, '2025-04-27 21:58:59'),
('02227790-88e7-476b-a024-7cbbea2af4c8', '1ff976d2-b5af-4585-9baf-f3f9bff3869c', 2, 'Master Python Programming', 'Complete a comprehensive Python fundamentals course.', NULL, '2025-04-27 21:58:59'),
('0f92bfa6-1799-4e5e-b394-64d3ea146ed1', 'ead65b8c-7cd3-4266-91c3-a2e6d1e5dac3', 1, 'HTML & CSS Fundamentals', 'Learn semantic HTML and responsive CSS layouts.', NULL, '2025-04-27 21:58:59'),
('1161ce63-6974-40a7-a58b-697df6e5345a', 'd0d0ed3e-a250-48a9-9cc8-9bf067231a21', 3, 'Kubernetes Orchestration', 'Deploy and manage containers at scale on Kubernetes.', NULL, '2025-04-27 21:58:59'),
('2358c538-a3e0-48af-9151-b488f8bdb7c1', '8399ffcb-dfef-4f5f-9bb7-168dceab4841', 3, 'Data Analysis with Pandas', 'Perform real-world data cleaning and exploratory analysis.', NULL, '2025-04-27 21:58:59'),
('29d19b89-0aa7-4726-9baf-fa1cffacfb03', 'd0d0ed3e-a250-48a9-9cc8-9bf067231a21', 1, 'Linux & Bash Essentials', 'Gain proficiency with Linux command line and shell scripting.', NULL, '2025-04-27 21:58:59'),
('29ef7677-16ae-468e-84b3-1d0b0b737121', 'ead65b8c-7cd3-4266-91c3-a2e6d1e5dac3', 4, 'State Management with Redux', 'Manage complex app state using Redux patterns.', NULL, '2025-04-27 21:58:59'),
('3c2bdff8-d48b-45be-bae6-a7da65cc71ec', '4a5ffc98-458b-4d7c-be77-ea0f345c0e33', 2, 'Linux Security Basics', 'Harden Linux systems and understand permissions.', NULL, '2025-04-27 21:58:59'),
('4b49e0be-b6e0-4254-9867-c1fc93c691d3', '8399ffcb-dfef-4f5f-9bb7-168dceab4841', 1, 'Learn Python for Data Science', 'Cover NumPy, Pandas, and data manipulation basics.', NULL, '2025-04-27 21:58:59'),
('4c5aa5ca-6bab-459b-abdc-aa36f57ded21', 'ead65b8c-7cd3-4266-91c3-a2e6d1e5dac3', 2, 'JavaScript ES6+ Features', 'Understand modern JS syntax, promises, and async/await.', NULL, '2025-04-27 21:58:59'),
('528d17f5-e209-4f41-bb72-8d470e6554d8', 'ead65b8c-7cd3-4266-91c3-a2e6d1e5dac3', 3, 'React.js Basics', 'Build component-based UIs with React and JSX.', NULL, '2025-04-27 21:58:59'),
('55ea7c75-c618-41c7-baee-978454561b53', '8399ffcb-dfef-4f5f-9bb7-168dceab4841', 4, 'Machine Learning Fundamentals', 'Learn supervised & unsupervised algorithms with scikit-learn.', NULL, '2025-04-27 21:58:59'),
('5dcfd264-5d20-40c2-99c3-646a7c76479d', '8399ffcb-dfef-4f5f-9bb7-168dceab4841', 5, 'Model Deployment with Flask', 'Wrap ML models into REST APIs using Flask or FastAPI.', NULL, '2025-04-27 21:58:59'),
('646c0bd1-cce3-48cb-ab19-d7cbb38dddff', '4a5ffc98-458b-4d7c-be77-ea0f345c0e33', 5, 'Security Monitoring & SIEM', 'Set up log aggregation and alerts with a SIEM tool.', NULL, '2025-04-27 21:58:59'),
('7bcf9028-48ed-4019-b5f9-966910072b1d', '1ff976d2-b5af-4585-9baf-f3f9bff3869c', 1, 'Learn Data Structures & Algorithms', 'Master common data structures and algorithms in your language of choice.', NULL, '2025-04-27 21:58:59'),
('7be58ce9-56c1-4447-b8ce-affe6208c8df', '4a5ffc98-458b-4d7c-be77-ea0f345c0e33', 4, 'Penetration Testing with Metasploit', 'Perform basic pentests using Metasploit Framework.', NULL, '2025-04-27 21:58:59'),
('846cec40-5407-482e-b97d-ed1a00076bc6', '1ff976d2-b5af-4585-9baf-f3f9bff3869c', 5, 'Implement CI/CD Pipelines', 'Set up continuous integration and delivery with Jenkins or GitHub Actions.', NULL, '2025-04-27 21:58:59'),
('b7dfc3c2-4554-49f3-acf2-4d8cbc3a28bf', '1ff976d2-b5af-4585-9baf-f3f9bff3869c', 4, 'Understand Database Systems', 'Learn SQL, schema design, and indexing strategies.', NULL, '2025-04-27 21:58:59'),
('b9906303-a0e2-417b-93d5-59b608a16bd4', '4a5ffc98-458b-4d7c-be77-ea0f345c0e33', 3, 'OWASP Top 10 Vulnerabilities', 'Study and practice preventing the OWASP Top 10 web flaws.', NULL, '2025-04-27 21:58:59'),
('d8a668fa-901d-4e7c-b9a7-8071802083ab', 'd0d0ed3e-a250-48a9-9cc8-9bf067231a21', 5, 'Infrastructure as Code with Terraform', 'Provision and manage cloud resources using Terraform.', NULL, '2025-04-27 21:58:59'),
('e3e8d14a-edb5-4448-8006-feba74fe1a9a', '1ff976d2-b5af-4585-9baf-f3f9bff3869c', 3, 'Build REST APIs with Flask', 'Develop and deploy RESTful APIs using Flask framework.', NULL, '2025-04-27 21:58:59'),
('e5cf6782-04ff-4485-b124-250b30bf0f0c', '8399ffcb-dfef-4f5f-9bb7-168dceab4841', 2, 'Statistics & Probability Basics', 'Understand descriptive stats, distributions, and hypothesis testing.', NULL, '2025-04-27 21:58:59'),
('eafe2fbd-2a8f-4038-843b-b3cd0f62a298', '4a5ffc98-458b-4d7c-be77-ea0f345c0e33', 1, 'Networking Fundamentals', 'Learn OSI model, TCP/IP, and common network protocols.', NULL, '2025-04-27 21:58:59'),
('eb342862-542b-41c1-9312-62b667df8116', 'ead65b8c-7cd3-4266-91c3-a2e6d1e5dac3', 5, 'Frontend Testing with Jest', 'Write unit and integration tests for React components.', NULL, '2025-04-27 21:58:59'),
('eee774f9-3776-4d0c-83dd-63d3db022d14', 'd0d0ed3e-a250-48a9-9cc8-9bf067231a21', 2, 'Docker Containerization', 'Containerize applications with Docker and write Dockerfiles.', NULL, '2025-04-27 21:58:59');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` char(36) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `is_mentor` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `name`, `email`, `created_at`, `is_mentor`) VALUES
('4c87d980-7457-4df1-ba12-c152b948b762', 'admin', 'scrypt:32768:8:1$WstwojMgummixFGV$de5f878e90cc64b1a9a35ea355ab94c63fa4226f35eae3227c1be829bf2daa17b0711d6cf72fb98d549f23b4ca7758850e2a51f5deaff65842f5d58cca0a6317', 'Administrator', 'admin@intrain.ai', '2025-06-20 14:06:04', 0);

-- --------------------------------------------------------

--
-- Table structure for table `user_roadmaps`
--

CREATE TABLE `user_roadmaps` (
  `id` char(36) NOT NULL,
  `user_id` char(36) NOT NULL,
  `roadmap_id` char(36) NOT NULL,
  `started_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_roadmap_progress`
--

CREATE TABLE `user_roadmap_progress` (
  `id` char(36) NOT NULL,
  `user_roadmap_id` char(36) NOT NULL,
  `step_id` char(36) NOT NULL,
  `completed_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `work_experiences`
--

CREATE TABLE `work_experiences` (
  `id` char(36) NOT NULL,
  `user_id` char(36) NOT NULL,
  `job_title` varchar(200) NOT NULL,
  `company_name` varchar(200) NOT NULL,
  `job_desc` text DEFAULT NULL,
  `start_month` tinyint(3) UNSIGNED NOT NULL COMMENT '1=Jan … 12=Dec',
  `start_year` smallint(5) UNSIGNED NOT NULL,
  `end_month` tinyint(3) UNSIGNED DEFAULT NULL COMMENT 'On Going - NULL',
  `end_year` smallint(5) UNSIGNED DEFAULT NULL COMMENT 'On Going - NULL',
  `is_current` tinyint(1) NOT NULL DEFAULT 0 COMMENT '1 = On Going',
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `achievements`
--
ALTER TABLE `achievements`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `roadmap_id` (`roadmap_id`);

--
-- Indexes for table `chat_evaluations`
--
ALTER TABLE `chat_evaluations`
  ADD PRIMARY KEY (`id`),
  ADD KEY `session_id` (`session_id`);

--
-- Indexes for table `chat_messages`
--
ALTER TABLE `chat_messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `session_id` (`session_id`);

--
-- Indexes for table `chat_sessions`
--
ALTER TABLE `chat_sessions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `hr_level_id` (`hr_level_id`);

--
-- Indexes for table `courses`
--
ALTER TABLE `courses`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `course_enrollments`
--
ALTER TABLE `course_enrollments`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ux_user_course` (`user_id`,`course_id`),
  ADD KEY `idx_user_id` (`user_id`),
  ADD KEY `idx_course_id` (`course_id`);

--
-- Indexes for table `cv_reviews`
--
ALTER TABLE `cv_reviews`
  ADD PRIMARY KEY (`id`),
  ADD KEY `submission_id` (`submission_id`);

--
-- Indexes for table `cv_review_sections`
--
ALTER TABLE `cv_review_sections`
  ADD PRIMARY KEY (`id`),
  ADD KEY `review_id` (`review_id`);

--
-- Indexes for table `cv_submissions`
--
ALTER TABLE `cv_submissions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `hr_levels`
--
ALTER TABLE `hr_levels`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `jobs`
--
ALTER TABLE `jobs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `mentorship_feedback`
--
ALTER TABLE `mentorship_feedback`
  ADD PRIMARY KEY (`id`),
  ADD KEY `session_id` (`session_id`);

--
-- Indexes for table `mentorship_sessions`
--
ALTER TABLE `mentorship_sessions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `mentee_id` (`mentee_id`),
  ADD KEY `mentor_id` (`mentor_id`);

--
-- Indexes for table `mentor_availabilities`
--
ALTER TABLE `mentor_availabilities`
  ADD PRIMARY KEY (`id`),
  ADD KEY `mentor_id` (`mentor_id`);

--
-- Indexes for table `mentor_profiles`
--
ALTER TABLE `mentor_profiles`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- Indexes for table `roadmaps`
--
ALTER TABLE `roadmaps`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `roadmap_steps`
--
ALTER TABLE `roadmap_steps`
  ADD PRIMARY KEY (`id`),
  ADD KEY `roadmap_id` (`roadmap_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `user_roadmaps`
--
ALTER TABLE `user_roadmaps`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `roadmap_id` (`roadmap_id`);

--
-- Indexes for table `user_roadmap_progress`
--
ALTER TABLE `user_roadmap_progress`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_roadmap_id` (`user_roadmap_id`),
  ADD KEY `step_id` (`step_id`);

--
-- Indexes for table `work_experiences`
--
ALTER TABLE `work_experiences`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_workexp_user` (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `hr_levels`
--
ALTER TABLE `hr_levels`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `achievements`
--
ALTER TABLE `achievements`
  ADD CONSTRAINT `achievements_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `achievements_ibfk_2` FOREIGN KEY (`roadmap_id`) REFERENCES `roadmaps` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `chat_evaluations`
--
ALTER TABLE `chat_evaluations`
  ADD CONSTRAINT `chat_evaluations_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `chat_sessions` (`id`);

--
-- Constraints for table `chat_messages`
--
ALTER TABLE `chat_messages`
  ADD CONSTRAINT `chat_messages_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `chat_sessions` (`id`);

--
-- Constraints for table `chat_sessions`
--
ALTER TABLE `chat_sessions`
  ADD CONSTRAINT `chat_sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `chat_sessions_ibfk_2` FOREIGN KEY (`hr_level_id`) REFERENCES `hr_levels` (`id`);

--
-- Constraints for table `course_enrollments`
--
ALTER TABLE `course_enrollments`
  ADD CONSTRAINT `fk_enroll_course` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`),
  ADD CONSTRAINT `fk_enroll_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `cv_reviews`
--
ALTER TABLE `cv_reviews`
  ADD CONSTRAINT `cv_reviews_ibfk_1` FOREIGN KEY (`submission_id`) REFERENCES `cv_submissions` (`id`);

--
-- Constraints for table `cv_review_sections`
--
ALTER TABLE `cv_review_sections`
  ADD CONSTRAINT `cv_review_sections_ibfk_1` FOREIGN KEY (`review_id`) REFERENCES `cv_reviews` (`id`);

--
-- Constraints for table `cv_submissions`
--
ALTER TABLE `cv_submissions`
  ADD CONSTRAINT `cv_submissions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `mentorship_feedback`
--
ALTER TABLE `mentorship_feedback`
  ADD CONSTRAINT `mentorship_feedback_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `mentorship_sessions` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `mentorship_sessions`
--
ALTER TABLE `mentorship_sessions`
  ADD CONSTRAINT `mentorship_sessions_ibfk_1` FOREIGN KEY (`mentee_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `mentorship_sessions_ibfk_2` FOREIGN KEY (`mentor_id`) REFERENCES `mentor_profiles` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `mentor_availabilities`
--
ALTER TABLE `mentor_availabilities`
  ADD CONSTRAINT `mentor_availabilities_ibfk_1` FOREIGN KEY (`mentor_id`) REFERENCES `mentor_profiles` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `mentor_profiles`
--
ALTER TABLE `mentor_profiles`
  ADD CONSTRAINT `mentor_profiles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `roadmap_steps`
--
ALTER TABLE `roadmap_steps`
  ADD CONSTRAINT `roadmap_steps_ibfk_1` FOREIGN KEY (`roadmap_id`) REFERENCES `roadmaps` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `user_roadmaps`
--
ALTER TABLE `user_roadmaps`
  ADD CONSTRAINT `user_roadmaps_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_roadmaps_ibfk_2` FOREIGN KEY (`roadmap_id`) REFERENCES `roadmaps` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `user_roadmap_progress`
--
ALTER TABLE `user_roadmap_progress`
  ADD CONSTRAINT `user_roadmap_progress_ibfk_1` FOREIGN KEY (`user_roadmap_id`) REFERENCES `user_roadmaps` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_roadmap_progress_ibfk_2` FOREIGN KEY (`step_id`) REFERENCES `roadmap_steps` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `work_experiences`
--
ALTER TABLE `work_experiences`
  ADD CONSTRAINT `fk_workexp_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
