from openai import OpenAI
import pandas as pd


class AIAnalyzer:
    """Handles OpenAI API integration for ad text analysis."""

    def __init__(self, api_key, prompt_text):
        """Initialize with API key and prompt text."""
        self.api_key = api_key
        self.prompt_text = prompt_text
        self.client = self._create_client()

    def _create_client(self):
        """Create and return an OpenAI client."""
        return OpenAI(api_key=self.api_key)

    def analyze_text(self, ad_text):
        """
        Analyze ad text using OpenAI API.
        Returns the analysis as a string.
        """
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[
                {"role": "user", "content": f"{self.prompt_text + ad_text}"}
            ]
        )

        return completion.choices[0].message.content

    def process_dataframe(self, df):
        """
        Process a DataFrame to analyze ad texts.
        Returns the DataFrame with AI analysis.
        """
        # Add AI analysis for ads without existing analysis
        df["AISays2"] = df.apply(
            lambda row: self.analyze_text(row["AdText"])
            if pd.isna(row.get("AISays")) or not row.get("AISays")
            else row.get("AISays"),
            axis=1
        )

        df["AISays"] = df["AISays"].fillna(df["AISays2"])
        df = df.drop(columns=["AISays2"])

        # Uncomment if you want to split the AI analysis into columns
        # df[["AIGarage", "AIAlert"]] = df["AISays"].str.split(" > ", expand=True)

        return df