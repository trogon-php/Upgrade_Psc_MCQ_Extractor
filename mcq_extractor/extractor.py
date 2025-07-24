import os
import json
import google.generativeai as genai


class MCQExtractor:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-pro")
        
    
    def extract_mcqs(self, batch_text,questions_to_ignore,custom_prompt,attempt=0):
      # if len(my_list) == 0:

        prompt = f"""
        You are an MCQ extractor.
        
      Extract all multiple-choice questions from the text below and return them as a JSON array.
      
      Each item in the array should include the following keys:
      - "SI.No": A serial number for the question.
      - "question": The full question, formatted as an HTML string. 
         - Wrap the main question in `<p>`.
         - If there are any statements (e.g., Statement I, II, etc.), include them inside the same HTML block with appropriate formatting.
         - If the question is a 'Match-the-Column' type, include both List I and List II inside the HTML, using `<ul>`, `<li>`, or `<table>` as needed.
      - "options": An array of strings, where each string is an option (e.g., [" Option 1", " Option 2"]).
      - "correct_answer": The CHAR identifier of the correct option (e.g., C), if provided in the answer key or generate correct according to question (Should not be null or anything , Mandatory!). there should only be answers as ["A", "B", "C", "D"].
      - "type": One of ['MCQ', 'Order-based', 'Match-the-Column'].
      - "category": One of the following, determined by analyzing the content of the question:
                * History
                * Geography
                * Economics
                * Indian Constitution
                * Kerala – Governance and System of Administration
                * Life Science and Public Health
                * Physics
                * Chemistry
                * Arts, Literature, Culture, Sports
                * Basics of Computer
                * Important Acts
                * Current Affairs
                * Simple Arithmetic, Mental Ability and Reasoning
                * General English
                * Malayalam language

            example : 
            [
               {    {
                    "SI.No": 13,
                    "question": "<p>A pilot is used to land on wide runways only. When approaching a smaller and/ or narrower runway, the pilot may feel he is at:</p>",
                    "options": [
                        "Greater height than he actually is with the tendency to land short.",
                        "Greater height and the impression of landing short.",
                        "Lower than actual height with the tendency to overshoot."
                    ],
                    "correct_answer": "A",
                    "type": "MCQ",
                    "category": "Life Science and Public Health"
                    }
                }
            ]
   
      Important formatting notes:
      - Include all contextual parts (statements, match-the-columns, etc.) **within the HTML in the "question" field**.
      - For questions with multiple statements, format them inside the HTML using `<ul>` or `<p>` tags as appropriate.
      - For match-the-column questions, display List I and List II in a clear, structured HTML format like a table or two lists.
      
      Note:
      - Correct any spelling or grammar issues in the extracted questions or statements based on context.
      - Ensure Proper Unicode fonts.
      - Ensure the output is a valid JSON array and properly structured.
      - Create questions or options (max 4), and statements - if contextually applicable and the chances to be created in the next or previous batches is lower (context is much higher in this batch)
      - if any questions happen to repeat , ignore it , (only ignore the questions with same purpose, not similar)
      Questions to ignore: (if no questions are present ignore!)
      \t{questions_to_ignore} \n
      These above questions should not be reprocessed or created again in this batch.!!
      
      Now extract from the following text:
        {batch_text}
        """

        extend_prompt_with="\n\tHere are some additional rules to follow:\n"
        if custom_prompt != "":
            extend_prompt_with += custom_prompt
            prompt += extend_prompt_with
         
        print(f"Sending batch to Gemini API... (Text length: {len(batch_text)} characters)")
        try:
            response = self.model.generate_content(prompt)
            raw_json_string = response.text.strip()

            # Strip markdown fences if they exist
            if raw_json_string.startswith("```json"):
                raw_json_string = raw_json_string[len("```json"):].strip()
            if raw_json_string.endswith("```"):
                raw_json_string = raw_json_string[:-len("```")].strip()

            ################################################################################################################################### raw_json_string+="af" ############################################################################################################################################################

            # Parse JSON to validate
            try:
                parsed_json = json.loads(raw_json_string)
                return parsed_json
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                if attempt<1:
                  print("calling api again.")
                  self.extract_mcqs(batch_text,questions_to_ignore,custom_prompt,1)


                return []

        except Exception as e:
            print(f"Error during MCQ extraction: {e}")
            return []
