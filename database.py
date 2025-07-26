import sqlite3

def create_connection():
    """Create a database connection to a SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect('meetings.db')
        print(f"SQLite version: {sqlite3.version}")
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn):
    """Create a table for storing meeting data."""
    try:
        sql_create_meetings_table = """
        CREATE TABLE IF NOT EXISTS meetings (
            id integer PRIMARY KEY,
            start_time text NOT NULL,
            summary text,
            transcript text,
            ai_summary text,
            key_takeaways text
        );
        """
        c = conn.cursor()
        c.execute(sql_create_meetings_table)
    except sqlite3.Error as e:
        print(e)

def add_meeting(conn, meeting_data):
    """Add a new meeting to the meetings table."""
    sql = ''' INSERT INTO meetings(start_time,summary,transcript,ai_summary,key_takeaways)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, meeting_data)
    conn.commit()
    return cur.lastrowid

def get_meeting_by_summary(conn, summary_keyword):
    """Query meetings by summary keyword."""
    cur = conn.cursor()
    cur.execute("SELECT * FROM meetings WHERE summary LIKE ?", ('%' + summary_keyword + '%',))
    rows = cur.fetchall()
    return rows

def main():
    conn = create_connection()
    if conn is not None:
        create_table(conn)
        # Example usage:
        # meeting = ('2025-07-22 10:00:00', 'Project Standup', 'This is the transcript.', 'This is the AI summary.', 'Key Takeaway: Project is on track.')
        # add_meeting(conn, meeting)
        # meetings = get_meeting_by_summary(conn, "Standup")
        # print(meetings)
        conn.close()
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()
