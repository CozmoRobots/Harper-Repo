import cozmo
import socket
import errno
import qrcode
import pyqrcode
from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol
from PIL import Image
from socket import error as socket_error
from cozmo.util import degrees, distance_mm, speed_mmps

#NOTE: in a terminal, open python
'''
import socket
s = socket.socket()
s.connect(('10.0.1.10', 5000))
s.sendall(b'message') or s.recv(4096)

'''

def cozmo_program(robot: cozmo.robot.Robot):
       
    # FOR SERVER:
    # s.sendall(b'message') to send messages
    # s.recv(4090) to receive messages
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket_error as msg:
        robot.say_text("socket failed" + msg).wait_for_completed()
    ip = "10.0.1.10"
    port = 5000
    
    try:
        s.connect((ip, port))
    except socket_error as msg:
        robot.say_text("socket failed to bind").wait_for_completed()
    cont = True
    
    robot.say_text("ready").wait_for_completed()

    
    # FOR CARDS:
    card1 = "" 
    card2 = ""
    
    # Card 1
    robot.camera.image_stream_enabled = True
    new_im = robot.world.wait_for(cozmo.world.EvtNewCameraImage)
    new_im.image.raw_image.show()

    #save the raw image as a bmp file
    img_latest = robot.world.latest_image.raw_image
    img_convert = img_latest.convert('L')
    img_convert.save("aPhoto.bmp")

    #save the raw image data as a png file, named imageName
    imageName = "myPhoto.png"
    img = Image.open("aPhoto.bmp")
    width, height = img.size
    new_img = img.resize( (width, height) )
    new_img.save( imageName, 'png')
    
    decodedPhoto = decode(Image.open('myPhoto.png'), symbols=[ZBarSymbol.QRCODE])
    
    if len(decodedPhoto) > 0:
        codeData = decodedPhoto[0] 
        myData = codeData.data 
        myString = myData.decode('ASCII')
        splitString = myString.split()
        card1 = splitString[0]
        card1suit = splitString[2]
        robot.say_text(myString).wait_for_completed()    
    else:
        robot.say_text("Could not decode data").wait_for_completed()
        return

    robot.say_text("Ready to see next card").wait_for_completed()
        
    # Card 2
    new_im = robot.world.wait_for(cozmo.world.EvtNewCameraImage)
    new_im.image.raw_image.show()

    #save the raw image as a bmp file
    img_latest = robot.world.latest_image.raw_image
    img_convert = img_latest.convert('L')
    img_convert.save("bPhoto.bmp")

    #save the raw image data as a png file, named imageName
    imageName = "myPhoto2.png"
    img = Image.open("bPhoto.bmp")
    width, height = img.size
    new_img = img.resize( (width, height) )
    new_img.save( imageName, 'png')
    
    decodedPhoto = decode(Image.open('myPhoto2.png'), symbols=[ZBarSymbol.QRCODE])
    
    if len(decodedPhoto) > 0:
        codeData = decodedPhoto[0] 
        myData = codeData.data 
        myString = myData.decode('ASCII')
        splitString = myString.split()
        card2 = splitString[0]
        card2suit = splitString[2]
        robot.say_text(myString).wait_for_completed()    
    else:
        robot.say_text("Could not decode data").wait_for_completed()
        return
    
    # grab index from card values for pair, then index of pair, [0] is string [1] is val
    cardValues = [("Two", 2), ("Three", 3), ("Four", 4), ("Five", 5),
                  ("Six", 6), ("Seven", 7), ("Eight", 8), ("Nine", 9), ("Ten", 10),
                  ("Jack", 10), ("Queen", 10), ("King", 10)]
    
        
    # Value determination
    numValue1 = 0 
    numValue2 = 0
    if (card1 != "Ace" and card2 != "Ace"):
        for values in cardValues:
            if values[0] == card1:
                numValue1 = values[1]
            if values[0] == card2:
                numValue2 = values[1]
        if numValue1 + numValue2 >= 14: #stay
            robot.say_text("Stay!").wait_for_completed()
            robot.drive_wheels(250, -250, None, None, 1.65)
        else:
            robot.say_text("Hit!").wait_for_completed()
            robot.set_lift_height(1).wait_for_completed()
    elif (card1 == "Ace"):
        for values in cardValues:
            if values[0] == card2:
                numValue2 = values[1]
        if numValue2 + 11 <= 21:
            if numValue2 + 11 >= 14:
                robot.say_text("Stay!").wait_for_completed()
                robot.drive_wheels(250, -250, None, None, 1.65)
            else:
                robot.say_text("Hit!").wait_for_completed()
                robot.set_lift_height(1).wait_for_completed()                
        else:
            robot.say_text("Hit!").wait_for_completed()
            robot.set_lift_height(1).wait_for_completed()
    elif (card2 == "Ace"):
        for values in cardValues:
            if values[0] == card1:
                numValue1 = values[1]
        if numValue1 + 11 <= 21:
            if numValue1 + 11 >= 14:
                robot.say_text("Stay!").wait_for_completed()
                robot.drive_wheels(250, -250, None, None, 1.65)
            else:
                robot.say_text("Hit!").wait_for_completed()
                robot.set_lift_height(1).wait_for_completed()                
        else:
            robot.say_text("Hit!").wait_for_completed()
            robot.set_lift_height(1).wait_for_completed()    
    
    # Transmit card info
    message = "Harper;" + card1 + "_" + card1suit + ";" + card2 + "_" + card2suit
    s.sendall(bytes(message, 'ascii'))
    
    return

cozmo.run_program(cozmo_program, use_viewer=False, force_viewer_on_top=False)