from pymilvus import Collection
def insert_resumes_to_data(resumeId:str,baseInfo:dict,skills_dict:dict,education_dict:dict,
                             projects:list,awards_text:str,overallSummary:list,workExperience:list,
                             collection_name="ai_interviewer_resumes"):
    collection=Collection(collection_name)
    data={
        "resumeId":resumeId,
        "name":baseInfo["name"],
        "city":baseInfo["city"],
        "skills":skills_dict,
        "education":education_dict,
        "awards":awards_text,
        "projects":projects,
        "workExperience":workExperience,
        "overallSummary":overallSummary
    }
    return data