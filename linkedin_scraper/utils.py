import pandas as pd


def list_of_job_to_pandas(job_list):
    dico_df = {
        "linkedin_url": [],
        "job_title": [],
        "company": [],
        "company_linkedin_url": [],
        "location": [],
        "posted_date": [],
        "applicant_count": [],
        "job_description": [],
        "benefits": [],
        "workplace_type": [],
        "experience": [],
    }
    for job in job_list:
        dico_this_job = job.to_dict()
        for key in dico_df.keys():
            dico_df[key].append(dico_this_job[key])
    df = pd.DataFrame.from_dict(dico_df)
    return df
