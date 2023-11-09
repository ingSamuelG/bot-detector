from scheduler import botScheduler
from bot_det import botDetector
from dotenv import load_dotenv


def main():
    load_dotenv()
    botReport = botDetector()
    # testy_1.__give_me_lines()
    # botReport.copy_prod_log()
    print(botReport.generate_bot_report())
    botReport.logHelper.ssh_server_con.close_conn()
    # my_scheduler = botScheduler()
    # my_scheduler.add_job(1, "S", job)
    # my_scheduler.add_job(1, "M", job2)
    # my_scheduler.run()


if __name__ == "__main__":
    main()
