# db.py or top of the file
import mysql.connector

class StudentOrgDBMS:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="jbcrossfire"
        )
        self.cursor = self.connection.cursor()
        self.create_database("student_org_db")
        self.use_database("student_org_db")
        self.create_tables()

    def destroy_database(self, name):
        self.cursor.execute(f"DROP DATABASE IF EXISTS {name}")

    def create_database(self, name):
        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {name}")

    def use_database(self, name):
        self.cursor.execute(f"USE {name}")

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `member` (
                `student_num` varchar(10) NOT NULL,
                `first_name` varchar(100),
                `last_name` varchar(100),
                `mem_username` varchar(30),
                `mem_password` varchar(50),
                `gender` char(1),
                `acad_year_enrolled` YEAR,
                `degree_prog` varchar(8),
                CONSTRAINT member_student_num_pk PRIMARY KEY(student_num),
                CONSTRAINT member_mem_username_uk UNIQUE KEY(mem_username)
            )""")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `organization` (
                `org_id` int(6) NOT NULL,
                `org_username` varchar(30),
                `org_password` varchar(50),
                `org_name` varchar(100),
                `year_founded` YEAR,
                `org_type` varchar(50) CHECK (org_type IN ('University', 'College', 'GS', 'N/A', 'NDMO', 'University-wide')),
                CONSTRAINT organization_org_id_pk PRIMARY KEY(org_id),
                CONSTRAINT organization_org_username_uk UNIQUE KEY(org_username)
            )""")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `joins` (
                `student_num` varchar(10) NOT NULL,
                `org_id` int(6) NOT NULL,
                `membership_status` varchar(20),
                `academic_year` YEAR,
                `classification` varchar(50), -- can put check
                `type` varchar(20), -- can put check
                `role` varchar(20), -- can put check
                `semester` varchar(1) CHECK (semester IN ('1', '2', 'M')),
                CONSTRAINT joins_student_num_fk FOREIGN KEY(student_num) REFERENCES member(student_num),
                CONSTRAINT joins_org_id_fk FOREIGN KEY(org_id) REFERENCES organization(org_id)
            )""")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `organization_event` (
                `org_id` int(6),
                `event_name` varchar(50),
                CONSTRAINT organization_event_org_id_fk FOREIGN KEY(org_id) REFERENCES organization(org_id),
                CONSTRAINT organization_event_org_event_name_uk UNIQUE KEY(event_name)
            )""")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `fee` (
                `trans_num` int(10) NOT NULL AUTO_INCREMENT,
                `amount` int,
                `due_date` DATE,
                `org_id` int(6) NOT NULL,
                CONSTRAINT fee_org_id_fk FOREIGN KEY(org_id) REFERENCES organization(org_id),
                CONSTRAINT fee_trans_num_pk PRIMARY KEY(trans_num)
            )""")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS `pays` (
                `student_num` varchar(10) NOT NULL,
                `trans_num` int(10) NOT NULL,
                `payment_status` varchar(10) CHECK (payment_status IN ('PAID', 'NOT PAID')),
                `payment_date` DATE,
                CONSTRAINT pays_student_num_fk FOREIGN KEY(student_num) REFERENCES member(student_num),
                CONSTRAINT pays_trans_num_fk FOREIGN KEY(trans_num) REFERENCES fee(trans_num)
            )""")
        
    def checkUsernamePassword(self, username, type):
        if type == "Member":
            self.cursor.execute("SELECT mem_password FROM member WHERE mem_username = %s", (username,))
        elif type == "Organization":
            self.cursor.execute("SELECT org_password FROM organization WHERE org_username = %s", (username,))
        return self.cursor.fetchone()

    def add_student(self, student_num, first_name, last_name, mem_username, mem_password, gender, acad_year_enrolled, degree_prog):
        self.cursor.execute("INSERT INTO member(student_num, first_name, last_name, mem_username, mem_password, gender, acad_year_enrolled, degree_prog) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (student_num, first_name, last_name, mem_username, mem_password, gender, acad_year_enrolled, degree_prog))
        self.connection.commit()

    def get_stud_num(self, username):
        self.cursor.execute("SELECT student_num FROM member WHERE mem_username = %s", (username,))
        return self.cursor.fetchone()
    
    def get_stud_name(self, student_num):
        self.cursor.execute("SELECT first_name, last_name FROM member WHERE student_num = %s", (student_num,))
        results = self.cursor.fetchone()
        if results:
            first_name, last_name = results
            return first_name, last_name
        return None, None
    
    def check_if_have_org(self, student_num):
        self.cursor.execute("SELECT o.org_name FROM organization o JOIN joins j ON o.org_id = j.org_id WHERE j.student_num = %s", (student_num,))
        result = self.cursor.fetchall()
        return result if result else None
    
    def get_org_id(self, org_name):
        self.cursor.execute("SELECT org_id FROM organization WHERE org_name = %s", (org_name,))
        return self.cursor.fetchone()
    
    def get_username(self, student_num):
        self.cursor.execute("SELECT mem_username FROM member WHERE student_num = %s", (student_num,))
        return self.cursor.fetchone()

    def get_all_payments(self, student_num):
        self.cursor.execute("SELECT p.trans_num, p.payment_status, p.payment_date FROM pays p JOIN member m ON p.student_num = m.student_num WHERE m.student_num = %s", (student_num,))
        result = self.cursor.fetchall()
        return result if result else None
    
    def get_org_id_username(self, username):
        self.cursor.execute("SELECT org_id FROM organization WHERE org_username = %s", (username,))
        return self.cursor.fetchone()

    def get_org_name(self, org_id):
        self.cursor.execute("SELECT org_name FROM organization WHERE org_id = %s", (org_id,))
        return self.cursor.fetchone()
    
    def get_org_events(self, org_id):
        self.cursor.execute("SELECT * FROM organization_event WHERE org_id = %s", (org_id,))
        result = self.cursor.fetchall()
        return result if result else None

    ###############################

    def get_students(self):
        self.cursor.execute("SELECT * FROM member")
        return self.cursor.fetchall()

    def add_organization(self, org_id, org_username, org_password, org_name, year_founded, org_type):
        self.cursor.execute("INSERT INTO organization (org_id, org_username, org_password, org_name, year_founded, org_type) VALUES (%s, %s, %s, %s, %s, %s)", (org_id, org_username, org_password, org_name, year_founded, org_type,))
        self.connection.commit()

    def get_organizations(self):
        self.cursor.execute("SELECT * FROM organization")
        return self.cursor.fetchall()
    
    def member_exists(self, student_num):
        self.cursor.execute("SELECT 1 FROM member WHERE student_num = %s", (student_num))
        return self.cursor.fetchone() is not None
    
    def org_exists(self, org_id):
        self.cursor.execute("SELECT 1 FROM organization WHERE org_id = %s", (org_id))
        return self.cursor.fetchone() is not None

    def add_membership(self, student_num, org_id, membership_status, acad_year, classification, joins_type, role, semester):
        self.cursor.execute("INSERT INTO joins (student_num, org_id, membership_status, academic_year, classification, type, role, semester) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (student_num, org_id, membership_status, acad_year, classification, joins_type, role, semester,))
        self.connection.commit()

    def get_memberships(self, org_id):
        self.cursor.execute("SELECT m.student_num, m.first_name, m.last_name, m.degree_prog FROM member m JOIN joins j ON m.student_num = j.student_num JOIN organization o ON j.org_id = o.org_id WHERE o.org_id = %s", (org_id,))
        return self.cursor.fetchall()

    # show current list of members
    def get_members(self, org_id):
        self.cursor.execute("""
            SELECT o.org_name, m.first_name, m.last_name, j.role
            FROM organization o
            JOIN joins j ON o.org_id = j.org_id
            JOIN member m ON j.student_num = m.student_num
            WHERE o.org_id = %s AND j.membership_status = 'ACTIVE'
        """, (org_id))
        return self.cursor.fetchall()

    # show organization events
    def get_events(self, org_id):
        self.cursor.execute("""
            SELECT o.org_name, e.event_name
            FROM organization o
            JOIN organization_event e ON o.org_id = e.org_id
            WHERE o.org_id = %s
            """, (org_id))
        return self.cursor.fetchall()
    
    def add_event(self, org_id, event_name):
        self.cursor.execute("INSERT INTO organization_event VALUES (%s, %s)", (org_id, event_name))
        self.connection.commit()

    def add_fee(self, trans_num, amount, due_date, org_id):
        self.cursor.execute("INSERT INTO fee VALUES (%s, %s, %s, %s)", (trans_num, amount, due_date, org_id))
        self.connection.commit()

    def add_pays(self, student_num, trans_num, payment_status, payment_date):
        self.cursor.execute("INSERT INTO pays VALUES (%s, %s, %s, %s)", (student_num, trans_num, payment_status, payment_date))
        self.connection.commit()

    # update membership information
    def update_membershipinfo(self, student_num, org_id, membership_status, academic_year, classification, type, role, semester):
        self.cursor.execute("UPDATE joins SET membership_status = %s, academic_year = %s, classification = %s, type = %s, role = %s, semester = %s", (membership_status, academic_year, classification, type, role, semester))
        self.connection.commit()

    # update event name
    def update_event(self, org_id, event_name):
        self.cursor.execute("UPDATE organization_event SET event_name = %s WHERE org_id = %s", (event_name, org_id))
        self.connection.commit()

    # update fee
    def update_fee(self, trans_num, amount, due_date, org_id):
        self.cursor.execute("UPDATE fee SET amount = %s, due_date = %s WHERE org_id = %s AND trans_num = %s", (amount, due_date, org_id, trans_num))
        self.connection.commit()
    
    # delete org event
    def delete_event(self, org_id, event_name):
        self.cursor.execute("DELETE from organization_event WHERE org_id = %s AND event_name = %s", (org_id, event_name))
        self.connection.commit()

######Additional features of student
    def get_memorg(self, student_num):
        self.cursor.execute("""
            SELECT org_name FROM organization o 
            JOIN joins j ON o.org_id=j.org_id 
            WHERE student_num = %s
        """, (student_num,))
        return self.cursor.fetchall()
    
    def add_memorg(self, student_num, org_id, membership_status, academic_year, classification, type, role, semester):
        self.cursor.execute("INSERT INTO joins (student_num, org_id, membership_status, academic_year, classification, type, role, semester) VALUES (%s, %s, %s, %s, %s,  %s, %s, %s)", (student_num, org_id, membership_status, academic_year, classification, type, role, semester))
        self.connection.commit()

    def get_member(self, student_num):
        self.cursor.execute("SELECT * FROM member WHERE student_num = %s", (student_num,))
        return self.cursor.fetchall()
    
    def update_member(self, mem_username, mem_password, degree_prog, student_num):
        self.cursor.execute("UPDATE member SET mem_username = %s, mem_password = %s, degree_prog = %s WHERE student_num = %s", (mem_username, mem_password, degree_prog, student_num))
        self.connection.commit()
    
    def get_pending(self, student_num):
        self.cursor.execute("""
        SELECT o.org_name, f.trans_num, f.amount, p.payment_status FROM fee f  JOIN pays p ON f.trans_num = p.trans_num  JOIN organization o ON f.org_id = o.org_id WHERE payment_status = 'NOT PAID' AND p.student_num = %s GROUP BY org_name, f.trans_num, f.amount, p.payment_status
        """, (student_num,))
        return self.cursor.fetchall()

# REPORTS TO BE GENERATED
    # 1 View all members of the organization by role, status, gender, degree program, batch (year of membership), and committee. (Note: we assume one committee membership only per organization per semester)
    def get_allmembers(self, org_id):
        self.cursor.execute("""
            SELECT o.org_id, o.org_name, m.student_num, m.first_name, m.last_name, m.gender, m.degree_prog, j.membership_status, j.academic_year, j.role, j.type
            FROM joins j
            JOIN organization o ON j.org_id = o.org_id
            JOIN member m ON j.student_num = m.student_num
            WHERE o.org_id = %s
            ORDER BY m.gender, m.degree_prog, j.academic_year, j.role, j.membership_status, j.type
            """, (org_id))
        return self.cursor.fetchall()

    # 2 View members for a given organization with unpaid membership fees or dues for a given semester and academic year.
    def get_unpaid_members(self, org_id, semester, academic_year, payment_status):
        self.cursor.execute("""
            SELECT m.student_num, m.first_name, m.last_name, m.acad_year_enrolled, j.semester, f.amount, f.due_date, p.payment_status, p.payment_date
            FROM pays p
            JOIN member m ON p.student_num = m.student_num
            JOIN fee f ON p.trans_num = f.trans_num
            JOIN joins j ON p.student_num = j.student_num AND f.org_id = j.org_id
            WHERE j.org_id = %s AND j.semester = %s AND j.academic_year = %s AND p.payment_status = 'NOT PAID'
            """, (org_id, semester, academic_year, payment_status))
        return self.cursor.fetchall()

    # 3 View a member's unpaid membership fees or dues for all their organizations (Member's POV).
    def get_unpaid_dues(self, student_num, payment_status):
        self.cursor.execute("""
            SELECT o.org_name, f.trans_num, f.amount, f.due_date, p.payment_status, j.org_id
            FROM pays p
            JOIN fee f ON p.trans_num = f.trans_num
            JOIN joins j ON p.student_num = j.student_num AND f.org_id = j.org_id
            JOIN organization o ON j.org_id = o.org_id
            WHERE p.student_num = %s AND p.payment_status = 'UNPAID'
            """, (student_num, payment_status))
        return self.cursor.fetchall()
    
    # 4 View all executive committee members of a given organization for a given academic year.
    def get_org_exec(self, org_id, acad_year_enrolled, role):
        self.cursor.execute("""
            SELECT m.student_num, m.first_name, m.last_name, m.acad_year_enrolled, j.org_id, j.role
            FROM joins j
            JOIN member m ON j.student_num = m.student_num
            WHERE j.org_id = %s AND m.acad_year_enrolled = %s AND j.role IN ('President', 'Vice President', 'Secretary', 'Treasurer', 'Auditor')
            """, (org_id, acad_year_enrolled, role))
        return self.cursor.fetchall()

    # 5 View all Presidents (or any other role) of a given organization for every academic year in reverse chronological order (current to past)
    def get_role_members(self, org_id, role):
        self.cursor.execute("""
            SELECT j.student_num, m.first_name, m.last_name, j.role, j.academic_year, j.semester
            FROM joins j
            JOIN member m ON j.student_num = m.student_num
            WHERE j.org_id = %s AND j.role = %s
            ORDER BY j.academic_year DESC
            """, (org_id, role))
        return self.cursor.fetchall()
    
    # 6 View all late payments made by all members of a given organization for a given semester and academic year
    def get_late_payments(self, org_id, academic_year, semester):
        self.cursor.execute("""
            SELECT p.student_num, m.first_name, m.last_name, p.trans_num, p.payment_date, f.due_date
            FROM pays p
            JOIN fee f ON p.trans_num = f.trans_num
            JOIN member m ON p.student_num = m.student_num
            JOIN joins j ON p.student_num = j.student_num AND f.org_id = j.org_id
            WHERE f.org_id = %s AND p.payment_status = 'PAID' AND p.payment_date > f.due_date AND j.academic_year = %s AND j.semester = %s
            """, (org_id, academic_year, semester))
        return self.cursor.fetchall()

    # 7 View the percentage of active vs inactive members of a given organization for the last n semesters
    def get_status_proportion(self, org_id):
        self.cursor.execute("""
            SELECT 
                type,
                COUNT(DISTINCT student_num) AS member_count,
                ROUND(
                    COUNT(DISTINCT student_num) * 100.0 /
                    (SELECT COUNT(DISTINCT student_num)
                    FROM joins
                    WHERE org_id = %s 
                    ORDER BY academic_year DESC, semester DESC
                    LIMIT '1'),
                2) AS percentage
            FROM joins
            WHERE org_id = ?
            ORDER BY academic_year DESC, semester DESC
            LIMIT '1'
            GROUP BY type""", (org_id))
        return self.cursor.fetchall()

    # 8 View all alumni members of a given organization as of a given date
    def get_current_alumni(self, org_id, year, semester):
        self.cursor.execute("""
            SELECT DISTINCT m.student_num, m.first_name, m.last_name, m.acad_year_enrolled
            FROM member m
            JOIN joins j ON m.student_num = j.student_num
            WHERE j.org_id = %s AND (j.academic_year < YEAR(%s) OR (j.academic_year = YEAR(%s) AND j.semester < %s)) AND j.classification = 'Alumni'
            """, (org_id, year, semester))
        return self.cursor.fetchall()
    
    # 9 View the total amount of unpaid and paid fees or dues of a given organization as of a given date
    def get_total_dues(self, org_id, payment_date):
        self.cursor.execute("""
            SELECT p.payment_status, SUM(f.amount) AS total_amount
            FROM pays p
            JOIN fee f ON p.trans_num = f.trans_num
            WHERE f.org_id = %s AND p.payment_date <= %s
            GROUP BY p.payment_status
            """, (org_id, payment_date))
        return self.cursor.fetchall()
    
    # 10 View all the member/s with the highest debt of a given organization for a given semester
    def get_higest_debt(self, org_id, academic_year, semester):
        self.cursor.execute("""
            SELECT p.student_num, m.first_name, m.last_name, SUM(f.amount) AS total_debt
            FROM pays p
            JOIN fee f ON p.trans_num = f.trans_num
            JOIN member m ON p.student_num = m.student_num
            JOIN joins j ON p.student_num = j.student_num AND f.org_id = j.org_id
            WHERE f.org_id = 101010  AND j.academic_year = 2025 AND j.semester = '2' AND p.payment_status = 'NOT PAID'
            GROUP BY p.student_num
            HAVING total_debt = (SELECT MAX(total_debt)FROM (SELECT p.student_num, SUM(f.amount) AS total_debt
                    FROM pays p
                    JOIN fee f ON p.trans_num = f.trans_num
                    JOIN joins j ON p.student_num = j.student_num AND f.org_id = j.org_id
                    WHERE f.org_id = %s
                    AND j.academic_year = %s
                    AND j.semester = %s
                    AND p.payment_status = 'NOT PAID'
                    GROUP BY p.student_num
                ) AS debts)""", (org_id, academic_year, semester))
        return self.cursor.fetchall()
