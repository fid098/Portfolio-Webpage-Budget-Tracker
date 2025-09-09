# PORTFOLIO WEBPAGE WITH BUDGET TRACKER INCORPORATED 
## VIDEO DEMO: https://youtu.be/zjQRF2EMWDc


#### PORTFOLIO WEBPAGE DESCRIPTION: The user is greeted with an index page that has buttons on the top right that allows the user to navigate the website. Below that is a table listing all my subjects taken and the grades i scored in each of them. In the about me page is a little information about me and below that is a table of most of my technical skills, soft skills, hobbies and below that is a button link to see my resume and img links to see my github, linkedin and gmail. In the experience page, the user am shown my past and present experience and achievements. In the projects page, the user is shown my past and present projects which include the budget tracker and in that includes a button that takes the user to the budget tracker webpage application.  

#### BUDGET TRACKER DESCRIPTION: Greeted with a login page, the user enters the system by logging in and can create an account if they do not have one. Once logged in, the user is greeted with an overview page which shows the current balance, total income, total expenses, money set out for rent, cash, savings, investments and miscellaneous. And below that the user is allowed to view previous transactions and can filter it for the last week, last month, last 6 months and the last year. In the transaction page, The user sees the current balance and the balance left to budget. Below that is an Add transaction session in which the user can enter an amount along with its description, date, category, budget category and type. If the type is income the money is added to the current balance and added to the balance left to budget. As that money is added bit by bit to each budget pot the balance left to budget reduces until it is 0 and all money is budgeted. Below that is a table showing all transactions and the total income, total expense and net balance. 

### **Portfolio Pages**
#### Index (index.html): landing page with navigation var and a table of my subject and grades. design choice: simple, welcoming layout to give immediate access to import sections 

#### About me (about.html): Short personal description + tables of (technical skills, soft skills, hobbies). Inclues links to resume, Github, Linkedin and gmail. design choice: centralized all personal/professional info to make it easy for recruiters. 

#### Projects (projects.html): cards showcasing projects, with descriptions hidden behind "show more" buttons for a cleaner look. includes a "budget tracker demo link". design choice: progressive disclosure- users only see more detail when they want it 

#### Experience (experience.html): lists my past and current experiences and achievements. design choice: timeline-style cards for clarity

### **Budget Tracker Pages**
#### Login (login.html): user authentication page. styled with bootstrap and custom css from chatgpt. users can log in or create an account 

#### Create Account (create_account.html): new users register with username, password(hashed) and name. Prevents duplicate usernames. 

#### Budget (budget.html): overview of: current balance, total income/expense, budget allocations (cash, rent , savings, investments, miscellaneous), remaining money left to allocate, transaction history (filterable by last 7 days, 1 month, 6 months, 1 year)

#### Transaction (transaction.html): add new transactions (income/expense) with description, date, category, and budget category. automatically checks if enough funds in a budget pot before subtracting. table view of all transactions + totals (income, expenses, net balance) 

#### Summary (summary.html): Pie chart(via Matplotlib + base64 encoding) for income distributions, expense distribution and budget allocation. Helps users visualize spending and budgeting patterns 

### **Backend (Flask and SQLite3)**
#### app.py: Handles all routes and logic. manages user sessions (Flask-Session). Passwords stored securely using "werkzeug.security". interacts with "users_information.db" for (users, transactions, categories and budget)

#### database tables: users- user accounts(id, username, hash, name), budget - (cash, rent, savings, investments, miscellaneous), categories - transaction categories(food, salary, utilities et.c), transactions - user transactions (linked to categories and budget)


### **Design choices and Justification**
#### Flask + SQLite: flask is lightweight and flexible so perfect for a personal project, swlite chosen for simplicity (no server setup, portable DB)

#### Boostrap: ensures responsive, mobile friendly UI, faster styling, consistent design across pages

#### Custom CSS(login.css, projects.css): allows fine-tuning beyoung Bootstrap defaults, example: centering login form

#### session management: prevent unauthorized access (redirects if not logged in), chose serve-side sessions (Flask-Session) for security

#### Charts with Matplotlib: Rendered as images, embessed in HTML. Chosen for simplicity and built in support, no extra JS libraries. 

## Running the Project 
### Prerequisites: Python 3.11.9, pip install flask flask-session werkzeug matplotlib 



