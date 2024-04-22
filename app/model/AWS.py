from app import app, db, s3_client
from uuid import uuid4
import json

import app.model.admin as admin

#TODO: maybe change aws s3 bucket to NO ACLs and limit access to this account.
def upload_media_file_to_s3(file_upload, user):
    filename = ""
    filename+=str(user.id)
    filename+="/"
    filename+=str(uuid4()) #safe file name: uuid4.
    s3_client.put_object(
        Bucket = str(app.config['BUCKET_NAME']),
        Key = filename,
        Body=file_upload,
        #ACL=str(app.config['ACL']),
        ContentType = file_upload.content_type
    )
    #output = 'https://s3-{}.amazonaws.com/{}/{}'.format(app.config['S3_REGION'], app.config['BUCKET_NAME'], filename)
    output = 'https://{}.s3.amazonaws.com/{}'.format(app.config['BUCKET_NAME'], filename)
    print(filename, output, file_upload.content_type)
    db.session.commit() #just in case

    dictFile = {}
    dictFile["type"] = "profilePicture"
    dictFile["fileInfo"] = [filename, file_upload.content_type]
    admin.logData(user.id,8,json.dumps(dictFile))

    return (output, filename)

def upload_resume_file_to_s3(file_upload, user):
    filename = ""
    filename+=str(user.id)
    filename+="/"
    filename+=str(uuid4()) #safe file name: uuid4.
    s3_client.put_object(
        Bucket = str(app.config['BUCKET_NAME_RESUME']),
        Key = filename,
        Body=file_upload,
        ContentType = file_upload.content_type
    )
    output = 'https://s3-{}.amazonaws.com/{}/{}'.format(app.config['S3_REGION'], app.config['BUCKET_NAME_RESUME'], filename)
    #print(filename, output, file_upload.content_type)
    db.session.commit() #just in case

    dictFile = {}
    dictFile["type"] = "resume"
    dictFile["fileInfo"] = [filename, file_upload.content_type]
    admin.logData(user.id,8,json.dumps(dictFile))

    return (output, filename)


def delete_profile_picture(user):
    if user.profile_picture is not None:
        s3_client.delete_object(Bucket=str(app.config["BUCKET_NAME"]), Key=user.profile_picture_key)
    user.set_profile_picture(None, None)
    db.session.commit()

def delete_intro_video(user):
    if user.intro_video is not None:
        s3_client.delete_object(Bucket=str(app.config["BUCKET_NAME"]), Key=user.intro_video_key)
    user.set_intro_video(None, None)
    db.session.commit()

def delete_resume(user):
    if user.resume is not None:
        s3_client.delete_object(Bucket=str(app.config["BUCKET_NAME_RESUME"]), Key=user.resume_key)
    user.set_resume(None, None)
    db.session.commit()


"""
The preferred way is to simply create a pre-signed URL for the image, and return a redirect to that URL. 
This keeps the files private in S3, but generates a temporary, time limited, URL that can be used to download the file directly from S3. 
That will greatly reduce the amount of work happening on your server, as well as the amount of data transfer being consumed by your server.
https://stackoverflow.com/questions/52342974/serve-static-files-in-flask-from-private-aws-s3-bucket
"""
def create_resume_link(user):
    if user.resume == None or user.resume_key == None:
        resumeUrl = None
    else:
        resumeUrl = s3_client.generate_presigned_url(
            'get_object', 
            Params = {'Bucket': str(app.config['BUCKET_NAME_RESUME']), 'Key': user.resume_key}, 
            ExpiresIn = 100
        )
    return resumeUrl