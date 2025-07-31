import pdfplumber
from .extractor import MCQExtractor

class MCQBatchProcessor:
    def __init__(self, api_key):
        self.extractor = MCQExtractor(api_key)
        self.pages_per_batch = 10
        self.max_questions_to_ignore = 10

    def get_total_pages(self, pdf_path):
        with pdfplumber.open(pdf_path) as pdf:
            return len(pdf.pages)
    
    def process_pdf_in_batches(self, pdf_path, custom_prompt):
        print(f"\nProcessing PDF: {pdf_path}")

        if custom_prompt:
            print("Using personalized instructions.")
        else:
            print("Using default instructions.")

        pdf_file = self.extractor.upload_pdf(pdf_path)
        total_pages = self.get_total_pages(pdf_path)
        all_extracted_questions = []
        questions_to_ignore = []

        for i in range(0, total_pages, self.pages_per_batch):
            start_page = i + 1
            end_page = min(i + self.pages_per_batch, total_pages)
            print(f"\nProcessing pages {start_page}-{end_page}...")

            if questions_to_ignore:
                print(f"Ignoring {len(questions_to_ignore)} questions from the previous batch.")

            batch_results = self.extractor.extract_mcqs_from_pages(
                pdf_file, start_page, end_page, custom_prompt, questions_to_ignore
            )

            if batch_results:
                all_extracted_questions.extend(batch_results)
                questions_to_ignore = batch_results[-self.max_questions_to_ignore:]
                print(f"Extracted {len(batch_results)} questions. Total: {len(all_extracted_questions)}")
            else:
                print("No questions extracted from this batch.")
                questions_to_ignore = []
        
        # Renumber questions sequentially
        for i, question in enumerate(all_extracted_questions):
            question['SI.No'] = i + 1

        print(f"\nTotal questions extracted: {len(all_extracted_questions)}")
        return all_extracted_questions
        
