#!/usr/bin/env python3

import os
import sys
from typing import List, Dict, Union, Optional

class Job:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
    
    def get_name(self) -> str:
        return self.name
    
    def get_description(self) -> str:
        return self.description
    
    def is_legal_job(self) -> bool:
        raise NotImplementedError("Subclasses must implement this method")


class LegalJob(Job):
    def __init__(self, name: str, description: str = "", rules: Optional[List[str]] = None):
        super().__init__(name, description)
        self.rules = rules or []
    
    def get_rules(self) -> List[str]:
        return self.rules
    
    def is_legal_job(self) -> bool:
        return True


class IllegalJob(Job):
    def __init__(self, name: str, description: str = "", punishment: str = ""):
        super().__init__(name, description)
        self.punishment = punishment or "Varies by jurisdiction"
    
    def get_punishment(self) -> str:
        return self.punishment
    
    def is_legal_job(self) -> bool:
        return False


class JobDatabase:
    def __init__(self):
        self.jobs: Dict[str, Union[LegalJob, IllegalJob]] = {}
        self.illegal_keywords = ["kill", "murder", "steal", "thief", "theft", "rob", "drug", "dealer", 
                              "hitman", "assassin", "traffic", "smuggl", "hack", "counterfeit", 
                              "fraud", "scam", "illegal", "criminal", "prostitut", "kidnap", "abduct",
                              "extort", "blackmail", "bribery", "launder", "terror"]
        self._load_default_jobs()
    
    def _load_default_jobs(self) -> None:
        self.add_legal_job(
            "Software Developer", 
            "Creates computer applications and systems",
            ["Maintain client confidentiality", "Adhere to data protection laws", "Follow ethical coding practices"]
        )
        self.add_legal_job(
            "Doctor", 
            "Practices medicine to diagnose and treat illness",
            ["Must be licensed", "Follow medical ethics", "Maintain patient confidentiality (HIPAA compliance)"]
        )
        self.add_legal_job(
            "Teacher", 
            "Provides education to students",
            ["Requires certification in most regions", "Must follow educational curriculum standards", "Duty of care to students"]
        )
        self.add_legal_job(
            "Lawyer", 
            "Provides legal counsel and representation",
            ["Must pass bar exam", "Follow legal ethics", "Maintain client-attorney privilege"]
        )
        self.add_illegal_job(
            "Drug Dealer", 
            "Sells illegal substances",
            "Felony charges with penalties ranging from 5 years to life imprisonment depending on substances and quantities"
        )
        self.add_illegal_job(
            "Hitman", 
            "Accepts payment to murder others",
            "Murder-for-hire is a felony with potential life imprisonment or death penalty"
        )
        self.add_illegal_job(
            "Human Trafficker", 
            "Illegally trades humans for exploitation",
            "Federal offense with 20 years to life imprisonment"
        )
        self.add_illegal_job(
            "Counterfeiter", 
            "Creates fake currency or documents",
            "Federal offense with up to 20 years imprisonment"
        )
        self.add_illegal_job(
            "Killer",
            "Kills people",
            "Murder is a felony with potential life imprisonment or death penalty"
        )
        self.add_illegal_job(
            "Murderer",
            "Deliberately kills someone",
            "Murder is a felony with potential life imprisonment or death penalty"
        )
        self.add_illegal_job(
            "Thief",
            "Steals others' property",
            "Theft can be classified as misdemeanor or felony depending on value, with penalties ranging from fines to imprisonment"
        )
        self.add_illegal_job(
            "Bank Robber",
            "Steals money from banks",
            "Federal offense with up to 20 years imprisonment, longer if weapons are used"
        )
        self.add_illegal_job(
            "Hacker",
            "Illegally accesses computer systems",
            "Computer fraud charges with up to 10 years imprisonment depending on the nature of the breach"
        )

    def add_legal_job(self, name: str, description: str, rules: List[str]) -> None:
        self.jobs[name.lower()] = LegalJob(name, description, rules)
    
    def add_illegal_job(self, name: str, description: str, punishment: str) -> None:
        self.jobs[name.lower()] = IllegalJob(name, description, punishment)
    
    def contains_illegal_keyword(self, job_name: str) -> bool:
        job_name_lower = job_name.lower()
        return any(keyword in job_name_lower for keyword in self.illegal_keywords)
    
    def check_job(self, job_name: str) -> Union[LegalJob, IllegalJob]:
        job_name = job_name.lower().strip()
        
        # Check for exact match first
        if job_name in self.jobs:
            return self.jobs[job_name]
        
        # Check for partial matches in existing jobs
        for existing_job in self.jobs:
            if job_name in existing_job or existing_job in job_name:
                return self.jobs[existing_job]
        
        # Check if the job contains illegal keywords
        if self.contains_illegal_keyword(job_name):
            return IllegalJob(
                job_name.title(),
                f"Activity involving illegal actions",
                "Likely illegal in most jurisdictions with penalties ranging from fines to imprisonment depending on specific actions"
            )
        
        # Default to legal with standard regulations
        return LegalJob(
            job_name.title(),
            "Assumed to be legal occupation",
            ["Follow local business regulations", "Obtain proper licensing if required", "Pay applicable taxes"]
        )


class CLI:
    def __init__(self):
        self.job_db = JobDatabase()
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        self.clear_screen()
        print("=" * 60)
        print(" " * 18 + "CAREER LEGALITY CHECKER")
        print("=" * 60)
        print()
    
    def print_result(self, job: Union[LegalJob, IllegalJob]):
        if job.is_legal_job():
            print(f"\n✓ LEGAL OCCUPATION: {job.get_name()}")
            print(f"\nDescription: {job.get_description()}")
            
            print("\nLEGAL REQUIREMENTS AND RULES:")
            for i, rule in enumerate(job.get_rules(), 1):
                print(f"  {i}. {rule}")
        else:
            print(f"\n✗ ILLEGAL OCCUPATION: {job.get_name()}")
            print(f"\nDescription: {job.get_description()}")
            
            print("\nLEGAL CONSEQUENCES:")
            print(f"  {job.get_punishment()}")
    
    def print_footer(self):
        print("\n" + "-" * 60)
        print("\nDISCLAIMER: This information is for educational purposes only.")
        print("Always consult with a legal professional for specific advice.")
    
    def run(self):
        while True:
            self.print_header()
            print("Enter a job to check its legality (or 'exit' to quit):")
            job_name = input("> ").strip()
            
            if job_name.lower() in ('exit', 'quit'):
                break
                
            if not job_name:
                continue
                
            job = self.job_db.check_job(job_name)
            self.print_result(job)
            self.print_footer()
            
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    CLI().run()