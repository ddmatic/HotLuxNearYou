from src.config import Config
from src.core.roman_converter import RomanConverter
from src.core.data_processor import DataProcessor
from src.services.scraper import Scraper
from src.utils.file_manager import FileManager
from src.core.apartment_tracker import ApartmentTracker
from src.services.ai_analyzer import AIAnalyzer
from src.secretconfig import APIKEY, PROMPTTXT


def main():
    """Main function to run the apartment tracking application."""
    # Initialize components
    config = Config()
    roman_converter = RomanConverter()
    data_processor = DataProcessor()
    scraper = Scraper(config, roman_converter)
    file_manager = FileManager(config)

    # Set to True to enable AI analysis
    DO_AI_STUFF = False

    # Initialize AI analyzer if enabled
    ai_analyzer = None
    if DO_AI_STUFF:
        ai_analyzer = AIAnalyzer(APIKEY, PROMPTTXT)

    # Initialize and run the apartment tracker
    tracker = ApartmentTracker(
        config=config,
        roman_converter=roman_converter,
        data_processor=data_processor,
        scraper=scraper,
        file_manager=file_manager,
        ai_analyzer=ai_analyzer
    )

    tracker.run()


if __name__ == "__main__":
    main()