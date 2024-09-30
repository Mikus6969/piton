import sqlite3

def parse_mbox(file_path):
    emails = []
    domains = []
    weekdays = []
    spam_confidences = []

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith("From:"):
                email = line.split()[1]
                emails.append(email)
                domains.append(email.split('@')[1])
            elif line.startswith("X-DSPAM-Confidence:"):
                spam_confidences.append(float(line.split()[1]))
            elif line.startswith("Date:"):
                parts = line.split()
                if len(parts) >= 3 and parts[2].isdigit():
                    weekday = parts[1][:-1]
                    weekdays.append(weekday)
    
    return emails, domains, weekdays, spam_confidences

# Function to create the SQLite database and tables
def create_database():
    conn = sqlite3.connect('email_data.db')
    cur = conn.cursor()
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Email (
        id INTEGER PRIMARY KEY,
        email TEXT UNIQUE
    )''')
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Domain (
        id INTEGER PRIMARY KEY,
        domain TEXT UNIQUE
    )''')
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Weekday (
        id INTEGER PRIMARY KEY,
        weekday TEXT UNIQUE
    )''')
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS SpamConfidence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id INTEGER,
        domain_id INTEGER,
        weekday_id INTEGER,
        confidence REAL,
        FOREIGN KEY (email_id) REFERENCES Email(id),
        FOREIGN KEY (domain_id) REFERENCES Domain(id),
        FOREIGN KEY (weekday_id) REFERENCES Weekday(id)
    )''')
    
    conn.commit()
    return conn, cur

# Function to insert data into the database
def populate_database(emails, domains, weekdays, spam_confidences, cur, conn):
    email_dict = {}
    domain_dict = {}
    weekday_dict = {}

    for email in emails:
        cur.execute('INSERT OR IGNORE INTO Email (email) VALUES (?)', (email,))
        cur.execute('SELECT id FROM Email WHERE email = ?', (email,))
        email_dict[email] = cur.fetchone()[0]

    for domain in domains:
        cur.execute('INSERT OR IGNORE INTO Domain (domain) VALUES (?)', (domain,))
        cur.execute('SELECT id FROM Domain WHERE domain = ?', (domain,))
        domain_dict[domain] = cur.fetchone()[0]

    for weekday in weekdays:
        cur.execute('INSERT OR IGNORE INTO Weekday (weekday) VALUES (?)', (weekday,))
        cur.execute('SELECT id FROM Weekday WHERE weekday = ?', (weekday,))
        weekday_dict[weekday] = cur.fetchone()[0]

    for i in range(len(emails)):
        cur.execute('''
        INSERT INTO SpamConfidence (email_id, domain_id, weekday_id, confidence)
        VALUES (?, ?, ?, ?)
        ''', (email_dict[emails[i]], domain_dict[domains[i]], weekday_dict[weekdays[i]], spam_confidences[i]))
    
    conn.commit()

# Function to print unique domains
def print_unique_domains(cur):
    cur.execute('SELECT domain FROM Domain')
    domains = cur.fetchall()
    print("Unique domains:")
    for domain in domains:
        print(domain[0])
    

# Function to retrieve and print emails received from a particular domain on Fridays and Saturdays
def print_emails_from_domain(cur):
    
    user_domain = input("Enter a domain name from the list above: ")
    
    # Retrieve emails received from the user-specified domain on Fridays and Saturdays
    cur.execute('''
    SELECT Weekday.weekday, Domain.domain, Email.email, SpamConfidence.confidence 
    FROM SpamConfidence
    JOIN Weekday ON SpamConfidence.weekday_id = Weekday.id
    JOIN Domain ON SpamConfidence.domain_id = Domain.id
    JOIN Email ON SpamConfidence.email_id = Email.id
    WHERE Domain.domain = ? AND Weekday.weekday IN ('Fri', 'Sat')
    ''', (user_domain,))
    
    rows = cur.fetchall()
    
    # Print the data nicely formatted with indentations in 4 columns
    print("\nE-mails received from {} on Fridays and Saturdays:".format(user_domain))
    print("{:<15} {:<25} {:<30} {:<20}".format("Day of the week", "Domain name", "E-mail address", "Spam confidence level"))
    for row in rows:
        print("{:<15} {:<25} {:<30} {:<20}".format(row[0], row[1], row[2], row[3]))

def main():
    file_path = 'mbox-short.txt'
    emails, domains, weekdays, spam_confidences = parse_mbox(file_path)
    conn, cur = create_database()
    populate_database(emails, domains, weekdays, spam_confidences, cur, conn)
    print_unique_domains(cur)
    print_emails_from_domain(cur)
    
    conn.close()

if __name__ == "__main__":
    main()

