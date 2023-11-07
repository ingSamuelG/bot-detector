from scheduler import botScheduler
from bot_det import testy
from dotenv import load_dotenv


def main():
    load_dotenv()
    testy_1 = testy()
    testy_1.give_me_lines()
    # my_scheduler = botScheduler()
    # my_scheduler.add_job(1, "S", job)
    # my_scheduler.add_job(1, "M", job2)
    # my_scheduler.run()


if __name__ == "__main__":
    main()
