from scheduler import botScheduler
from bot_det import botDetector
from dotenv import load_dotenv


def main():
    load_dotenv()
    botReport = botDetector()
    botReport.generate_bot_report()


if __name__ == "__main__":
    main()
