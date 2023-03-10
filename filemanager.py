#!/bin/python2

from datetime import datetime
import dateutil.relativedelta
import os
import logging
import smtplib
from email.mime.multipart import MIMEMultipart

mail_server = "localhost"
mail_from = "filearchiver@abc.com"
mail_to = "<email_receiver@<domain>.com"

def send_mail(status):
        if status == 'passed':
                message = MIMEMultipart("alternative")
                message["Subject"] = "Disk usage is same"
        elif status == 'failed':
                message = MIMEMultipart("alternative")
                message["Subject"] = "Disk usage different"


        message["From"] = mail_from
        message["To"] = mail_to
        email = smtplib.SMTP(mail_server)
        email.sendmail(mail_from, mail_to, message.as_string())



logging.basicConfig(level=logging.INFO)

d1 = datetime.now()
current_date = d1.strftime('%Y%m%d')
folder_date = d1.strftime('%Y%m%d_%H%M%S')
logging.info("Current date is : " + current_date)
d2 = d1 - dateutil.relativedelta.relativedelta(months=4)
end_date = d2.strftime('%Y%m%d')
logging.info("End date is : " + end_date)

script_dir = '/home/healthchk/systemcheck/inode_script/' # Place where script stored
move_src_dir = '/home/healthchk/systemcheck/excel_files/' # Directory that contains files to be archived
move_dst_dir = '/home/healthchk/systemcheck/dest_files/' # Temporary folder used to store files which filters with respective months
move_dst_fol = move_dst_dir + folder_date  # In temporary folder new folder will be created with todays date time

if os.path.exists(move_dst_fol):
	logging.info('File moving directory exists')
else:
	logging.info('File moving directory does not exists')
	logging.info('directory created for file moving')
	os.makedirs(move_dst_fol)

for i in range(4, 16, 1):
	d2 = d1 - dateutil.relativedelta.relativedelta(months=i)
	acm = d2.strftime('%Y%m%d')
	archive_date = acm[:6]
	move_src_path = move_src_dir + archive_date
	command_move = 'cp -r {}* {} 2>/dev/null'.format(move_src_path, move_dst_fol)
	os.system(command_move)
	logging.info(archive_date +' Moved to the Destination directory') 

cmd_disk_usage_1 = 'du -s {}'.format(move_dst_fol)
p = os.popen(cmd_disk_usage_1)
p2 = p.read()
p.close()
p3 = p2.split('	')
first_usage =  str(p3[0])
if first_usage != 0:
	logging.info("Disk Usage in moved files :" + first_usage)
else:
	logging.warning("Disk usage in moved files is 0")
os.chdir(move_dst_dir)
command_tar_file = 'tar -czf {}.tar.gz {} '.format(folder_date, folder_date)
logging.info('Created zipped file')
os.system(command_tar_file)


tar_file_copy_path = '/home/healthchk/systemcheck/archives' # Directory path which stores the the archive files
tar_file_copy_dir = '/home/healthchk/systemcheck/archives/' # Directory which store archive files
logging.info('Checking for archive folder exists or not')
if os.path.exists(tar_file_copy_path):
    logging.info('Archive directory exists')
    tar_file = folder_date + '.tar.gz'
    logging.info('Checking for zipped file')

    if os.path.exists(tar_file):
        logging.info("Zip file " + tar_file + " Found")
        cmd_move_tar_file = 'mv {} {}'.format(tar_file, tar_file_copy_path)
        os.system(cmd_move_tar_file)
        logging.info("Zipped file moved to the archive directory")
    else:
        logging.warning("Zip file " + tar_file + " Not found" )
else:
    logging.info('Archive directory doesnot exists')
    os.makedirs(tar_file_copy_path)
    logging.info('Created archive directory')
    logging.info('Checking for zipped file')
    if os.path.exists(tar_file):
        logging.info("Zip file " + tar_file + " Found")
        cmd_move_tar_file = 'mv {} {}'.format(tar_file, tar_file_copy_path)
        os.system(cmd_move_tar_file)
        logging.info("Zipped file moved to the archive directory")
    else:
        logging.warning("Zip file " + tar_file + " Not found" )

os.chdir(script_dir)

tar_file_tmp_copy_path = '/home/healthchk/systemcheck/inode_script/temp'
tar_file_tmp_copy_dir = '//home/healthchk/systemcheck/inode_script/temp/'
logging.info('Checking for temp directory')
if os.path.exists(tar_file_tmp_copy_path):
	logging.info('temp file exists and deleting temp directory')
	cmd_rm_tem_dir = 'rm -rf {}'.format(tar_file_tmp_copy_path)
	os.system(cmd_rm_tem_dir)
	os.makedirs(tar_file_tmp_copy_path)
	logging.info('New temp directory created')
else:
	os.makedirs(tar_file_tmp_copy_path)
	logging.info('temp directory doesnot exists')
	logging.info('New temp directory created')
	
tar_file = tar_file_copy_dir + folder_date + '.tar.gz'
if os.path.exists(tar_file):
	logging.info('Checking zipped file to verfy its content size')
	cmd_cp_tar_file = 'cp {} {}'.format(tar_file, tar_file_tmp_copy_path)
	os.system(cmd_cp_tar_file)
	logging.info('Zipped file copied to the temp directory')

temp_tar_file = folder_date + '.tar.gz'

os.chdir(tar_file_tmp_copy_dir)
cmd_untar_file = 'tar -xzf {} '.format(temp_tar_file)
os.system(cmd_untar_file)
logging.info('Unzipped the file')
os.chdir(script_dir)


temp_untar_dir = tar_file_tmp_copy_dir  + folder_date
logging.info('Getting the disk usage for unzipped file')
cmd_disk_usage_2 = 'du -s {}'.format(temp_untar_dir)
p3 = os.popen(cmd_disk_usage_2)
p4 = p3.read()
p3.close()
p5 = p4.split('	')
second_usage =  str(p5[0])
logging.info('Disk usage in unzipped file : ' + second_usage)
logging.info('Checking disk is same or not')

if first_usage == second_usage:
	logging.info("Disk usage is same")
	cmd_rm_temp_folder = 'rm -rf temp'
	os.system(cmd_rm_temp_folder)
	send_mail('passed')

else:
	logging.warning("Disk usage is not same")
	send_mail('failed')





