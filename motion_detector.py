import cv2
import datetime
import pandas


first_frame=None
status_list=[None,None]
time_list=[]

df=pandas.DataFrame(columns=["Start","End"])

camera=cv2.VideoCapture(0)

fourcc = cv2.VideoWriter_fourcc(*'XVID') 
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480)) 

while True:
    status=0 #
    check,frame = camera.read()

    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    gray=cv2.GaussianBlur(gray,(21,21),0)

    if first_frame is None:
        first_frame=gray
        continue

    delta_frame=cv2.absdiff(first_frame,gray)
    threshhold_frame=cv2.threshold(delta_frame,30,255,cv2.THRESH_BINARY)[1]
    threshhold_frame=cv2.dilate(threshhold_frame,None,iterations=2)

    (_,cnts,_)=cv2.findContours(threshhold_frame.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    for contour in cnts:
        if cv2.contourArea(contour)<10000:
            continue
        out.write(frame)#write the frame to video file
        status=1
        (x,y,w,h)=cv2.boundingRect(contour)
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),3)

    status_list.append(status)
    status_list=status_list[-2:]#otherwise memory issues can happen with long video

    if status_list[-1]==1 and status_list[-2]==0:
        time_list.append(datetime.datetime.now())
    if status_list[-1]==0 and status_list[-2]==1:
        time_list.append(datetime.datetime.now())

    cv2.imshow("Color Frame",frame)
    cv2.imshow("Gray Frame",gray)
    cv2.imshow("Delta Frame",delta_frame)
    cv2.imshow("Thresh",threshhold_frame)

    key=cv2.waitKey(1)
    if key==ord('q'):
        if status==1:
            status_list.append(datetime.datetime.now())
        break
print(status_list)
print(time_list)
for i in range(0,len(time_list),2):
    df=df.append({"Start":time_list[i],"End":time_list[i+1]},ignore_index=True)

df.to_csv("Times.csv")
print(df)

camera.release()
cv2.destroyAllWindows()


#Make html bokeh time chart
df=pandas.read_csv('Times.csv')
df['Start'] = pandas.to_datetime(df['Start'])
df['End'] = pandas.to_datetime(df['End'])

