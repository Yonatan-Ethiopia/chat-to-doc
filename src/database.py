import sqlite3 as sql3
from pathlib import Path
import hashlib
import disk_mgr as mgr

class initdb:
	def __init__(self):
		mgr.get_db()
		conn = sql3.connect(Path("db/jobs.db"))
		cursor = conn.cursor()
		cursor.execute('''
			CREATE TABLE IF NOT EXISTS jobs_table(
				id TEXT PRIMARY KEY,
				user_id TEXT,
				file_name TEXT DEFAULT file,
				md_path TEXT,
				epub_path TEXT DEFAULT None,
				status TEXT DEFAULT PENDING,
				created_at DATETIME DEFAULT CURRENT_TIMESTAMP
			)
		''')
		conn.commit()
		cursor.close()
		conn.close()
	def gen_id(self, file_name):
		unique_id = hashlib.sha256(file_name.encode('utf-8')).hexdigest()
		return unique_id
	def create_job(self, file_name, user_id, md_path):
		job_id = self.gen_id(file_name)
		if mgr.is_workspace(job_id):
			return job_id
		conn = sql3.connect(Path("db/jobs.db"))
		cursor = conn.cursor()
		sql_insert = """
			INSERT INTO jobs_table (id, user_id, file_name, md_path,epub_path, STATUS) VALUES (?,?,?,?,?,?)
			"""
		cursor.execute(sql_insert, (job_id, user_id, file_name, md_path,f"/home/yonatan/Bdoc/epubs/{job_id}.epub","PENDING"))
		conn.commit()
		cursor.close()
		conn.close()
		return job_id
	def update_status(self, job_id, status):
		conn = sql3.connect(Path("db/jobs.db"))
		cursor = conn.cursor()
		cursor.execute("UPDATE jobs_table SET status = ? WHERE id = ?", (status, job_id))
		conn.commit()
		cursor.close()
		conn.close()
def check_status(job_id):
	conn = sql3.connect("db/jobs.db")
	conn.row_factory = sql3.Row
	cursor = conn.cursor()
	
	cursor.execute("SELECT status FROM jobs_table WHERE id = ?", (job_id,))
	
	row = cursor.fetchone()
	conn.close()
	
	if row:
		return row['status']
	return None
def get_epub_path(job_id):
	conn = sql3.connect("db/jobs.db")
	conn.row_factory = sql3.Row
	cursor = conn.cursor()
	cursor.execute("SELECT epub_path FROM jobs_table WHERE id = ?", (job_id,))
	row = cursor.fetchone()
	conn.close()
	if row:
		return row['epub_path']
	return None

def get_epub_name(job_id):
	conn = sql3.connect("db/jobs.db")
	conn.row_factory = sql3.Row
	cursor = conn.cursor()
	cursor.execute("SELECT file_name FROM jobs_table WHERE id = ?",(job_id,))
	row = cursor.fetchone()
	conn.close()
	if row:
		return row['file_name']
	return None   
def claim_next_job():
	conn = sql3.connect("db/jobs.db")
	conn.row_factory = sql3.Row
	cursor = conn.cursor()
	query = """
	UPDATE jobs_table 
	SET status = 'PROCESSING'
	WHERE id = (
		SELECT id FROM jobs_table WHERE status = 'PENDING' 
		ORDER BY created_at ASC LIMIT 1
	)
	RETURNING id, md_path;
	"""
	try:
		cursor.execute(query)
		job = cursor.fetchone()
		conn.commit()
		return job
	except Exception as e:
		print(f"Claiming job failed :{e}")
		return None
	finally:
		cursor.close()
		conn.close()
