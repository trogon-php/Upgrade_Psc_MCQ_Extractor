import pdfplumber
import re
from .extractor import MCQExtractor


class MCQBatchProcessor:
    def __init__(self, api_key):
        self.extractor = MCQExtractor(api_key)
        self.pages_per_batch = 15
        self.max_chars_per_batch = 15000  # Adjust based on token limits
        self.max_questions_to_ignore = 10  # Conservative limit to avoid token overload
        
    def match_patterns(self, text):
        patterns = [
            r'^\d+\.\s*(.+?)$',                 # 1. Question text
            r'^Q\d+[.:]?\s*(.+?)$',             # Q1: or Q1. Question text
            r'^Question\s*\d+[.:]?\s*(.+?)$',   # Question 1: Question text
            r'^\(\d+\)\s*(.+?)$',               # (1) Question text
            r'^\d+\)\s*(.+?)$',                 # 1) Question text
        ]
        for pattern in patterns:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                return True
        return False
    
    def count_questions_in_text(self, text):
        """Count questions in a given text"""
        lines = text.split('\n')
        question_count = 0
        
        for line in lines:
            line = line.strip()
            if line and self.match_patterns(line):
                question_count += 1
        
        return question_count
    
    def create_page_based_batches(self, pdf_path):
        """Create batches based on pages (5 pages per batch) without overlap"""
        print("Creating page-based batches...")
        
        batches = []
        
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"Total pages in PDF: {total_pages}")
            
            # Create batches of pages without overlap
            for i in range(0, total_pages, self.pages_per_batch):
                batch_start_page = i
               #  batch_start_page = max(0, i - 1) if i > 0 else 0
                batch_end_page = min(i + self.pages_per_batch, total_pages)
                
                # Extract text from pages in this batch
                batch_text = ""
                for page_num in range(batch_start_page, batch_end_page):
                    page_text = pdf.pages[page_num].extract_text()
                    if page_text:
                        batch_text += f"\n--- Page {page_num + 1} ---\n"
                        batch_text += page_text + "\n"
                
                # Count questions in this batch
                question_count = self.count_questions_in_text(batch_text)
                
                # Create batch object
                batch = {
                    'batch_number': len(batches) + 1,
                    'start_page': batch_start_page + 1,  # 1-indexed for display
                    'end_page': batch_end_page,          # 1-indexed for display
                    'text': batch_text,
                    'question_count': question_count,
                    'char_count': len(batch_text)
                }
                
                batches.append(batch)
                
                print(f"Created batch {batch['batch_number']}: Pages {batch['start_page']}-{batch['end_page']} "
                      f"({question_count} questions, {len(batch_text)} chars)")
        
        return batches
    
    def process_pdf_in_batches(self, pdf_path, custom_prompt):
        """Main function to process PDF in page-based batches"""
        print("\n\t\t Processing PDF ", pdf_path, "\t\t")

        # Check if the response is yes, and then prompt for the additional instructions
        if custom_prompt != ""  and custom_prompt != None:
            print("Proceeding with personalized instructions")
        else:
            print("Proceeding with in-built instructions.")

        
        # Create page-based batches
        batches = self.create_page_based_batches(pdf_path)
        print(f"Created {len(batches)} batches")
        
        if not batches:
            print("No batches created")
            return []
        
        # Process each batch
        all_extracted_questions = []
        questions_to_ignore = []  # Questions to ignore in next batch
        questions_to_remember = 0  # Calculate no from first batch only 
        
        for batch in batches:
            print(f"\nProcessing batch {batch['batch_number']} (Pages {batch['start_page']}-{batch['end_page']})...")
            print(f"Questions expected in this batch: {batch['question_count']}")
            
            if batch['question_count'] == 0:
                print("No questions found in this batch, skipping...")
                continue
            
            # Check if batch is too large #############################
            if batch['char_count'] > self.max_chars_per_batch:
                print(f"Warning: Batch {batch['batch_number']} is large ({batch['char_count']} chars). "
                      f"Consider reducing pages_per_batch.")
            
            # Show ignore list info
            if questions_to_ignore:
                print(f"Ignoring {len(questions_to_ignore)} questions from previous batch")
            
            ###################### Extract MCQs from this batch (pass questions_to_ignore to extractor) GEMINI CALL ######################
            batch_results = self.extractor.extract_mcqs(batch['text'], questions_to_ignore,custom_prompt)
            
            # Calculate no questions_to_remember ONLY from first batch
            if batch['batch_number'] == 1:
                pages_in_batch = batch['end_page'] - batch['start_page'] + 1
                questions_per_page = len(batch_results) / pages_in_batch if pages_in_batch > 0 else 0
                questions_to_remember = min(int(questions_per_page), self.max_questions_to_ignore)
               #  print(f"Will remember {questions_to_remember} questions from each batch (calculated from first batch)")
            
            # Prepare questions to ignore for next batch
            if len(batch_results) >= questions_to_remember:
                questions_to_ignore = batch_results[-questions_to_remember:]
            else:
                questions_to_ignore = batch_results.copy()  # Send all if batch has fewer questions
            
            print(f"Extracted {len(batch_results)} questions from batch {batch['batch_number']}")
            print(f"Will ignore {len(questions_to_ignore)} questions in next batch")
            
            all_extracted_questions.extend(batch_results)
            print("")
        
        # Renumber questions sequentially
        for i, question in enumerate(all_extracted_questions):
            question['SI.No'] = i + 1
        
        print(f"\nTotal questions extracted: {len(all_extracted_questions)}")
        return all_extracted_questions
