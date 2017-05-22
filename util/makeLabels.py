import os
import sys
import shutil
import pymysql.cursors

SQL = """ 
	SELECT
		CASE class  
			WHEN 'ordersign' THEN '0' 
	        WHEN '20limit' THEN '1' 
	        WHEN '30limit' THEN '1' 
	        WHEN '40limit' THEN '1' 
	        WHEN '50limit' THEN '1' 
	        WHEN '70limit' THEN '1' 
	        ELSE '1'  
		END as num_class,
		bbox_x1_center_ratio,
		bbox_y1_center_ratio,
		bbox_width_ratio,
		bbox_height_ratio,
		image_path
	FROM items
	WHERE class IN ('ordersign', '20limit', '30limit', '40limit', '50limit', '70limit')
""" 

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='root',
    db='Routeshoot',
    cursorclass=pymysql.cursors.DictCursor)


def newDir(name):	
	if os.path.exists(name):
		shutil.rmtree(name)
	os.makedirs(name)

newDir('train');
newDir('train/labels');
newDir('train/images');


with connection.cursor() as cursor:
	cursor.execute(SQL)
	for row in cursor.fetchall():
		file = os.path.basename(row['image_path'])
		fileName, fileExtension = os.path.splitext(file)
		
		shutil.copy(row['image_path'], 'train/images')

		train = open('train/train.txt','a')
		train.write(os.getcwd() + '/train/images/' + file + "\n")
		train.close()
        
		file = open('train/labels/'+ fileName +'.txt','a')
		string = (' ').join([row['num_class'], row['bbox_x1_center_ratio'], row['bbox_y1_center_ratio'], row['bbox_width_ratio'], row['bbox_height_ratio']])
		file.write(string)
        file.close()