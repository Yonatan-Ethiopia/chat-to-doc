import database
import converter
import time
db = database.initdb()

def start_worker():
	while True:
		job = database.claim_next_job()
		if job:
			job_id = job["id"]
			md_path = job["md_path"]
			try:
				converter.convert(job_id, md_path)
				print("complete")
				
			except Exception as e:
				db.update_status(job_id, "FAILED")
		else:
			time.sleep(5)
if __name__ == "__main__":
	start_worker()
