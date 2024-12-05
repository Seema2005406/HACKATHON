import logging
from types import *
import time
import threading
import subprocess
from utility import MyCarMaker, MyDockerDigitalAuto
import os

class DemoController:
    def __init__(self):        
        self.Car_Maker_Object    = MyCarMaker()
        self.Digital_Auto_Object = MyDockerDigitalAuto()

        self.thread_1 = threading.Thread(target = self.Observe_Value_From_Digital_Auto)
        self.thread_2 = threading.Thread(target = self.Trigger_Actions)

        self.thread_1.start()
        self.thread_2.start()

        self.thread_1.join()
        self.thread_2.join()
 
    def Observe_Value_From_Digital_Auto(self):
        while True:
            self.Digital_Auto_Object.Get_Signal()
            time.sleep(2)
    
    def Trigger_Actions(self):        
        while True:
           # if (self.Digital_Auto_Object.Kuksa_Signals["CM_control"][1] == True #and
                #self.Car_Maker_Object.CM_State == #self.Car_Maker_Object.State.Stop.value):

                self.CarMaker_Flow_Control()
            
            #print("Waiting for user request")

            time.sleep(2)

    def CarMaker_Flow_Control(self):
        self.Car_Maker_Object.Open_In_Windows()
        # Get Signal From Car Maker
        self.Get_Data_From_CarMaker_To_DB()
        # Set Signal to Digital Auto
        self.Digital_Auto_Object.Set_Signal()

        self.Car_Maker_Object.Connect()
        self.Car_Maker_Object.Load_Test_Run()
        self.Car_Maker_Object.Start_Simulation()

        self.Run_Simulation_And_Check_Stop_Condition()
        
        self.Car_Maker_Object.Stop_Simulation()

        self.Car_Maker_Object.Close()

        self.Digital_Auto_Object.Kuksa_Signals["CM_gas"][1]     = 0
        self.Digital_Auto_Object.Kuksa_Signals["CM_destrq"][1]      = 0
        self.Digital_Auto_Object.Kuksa_Signals["CM_vehspd"][1]           = 0
        self.Digital_Auto_Object.Kuksa_Signals["CM_acttrq"][1]   = 0
        self.Digital_Auto_Object.Kuksa_Signals["CM_destrq"][1]    = 0
        self.Digital_Auto_Object.Kuksa_Signals["CM_brakepr"][1]    = 0
        self.Digital_Auto_Object.Kuksa_Signals["CM_braketrq"][1]    = 0

        self.Digital_Auto_Object.Set_Signal()
        time.sleep(1)

    # Define the scenario of Demo here
    def Run_Simulation_And_Check_Stop_Condition(self):

            # Get Signal From Car Maker
            self.Get_Data_From_CarMaker_To_DB()
            # Set Signal to Digital Auto
            self.Digital_Auto_Object.Set_Signal()

            time.sleep(0.5)

    def Get_Data_From_CarMaker_To_DB(self):
        try:
            self.Digital_Auto_Object.Kuksa_Signals["CM_gas"][1] = self.Car_Maker_Object.CM_Signals["gas"][1]

            self.Digital_Auto_Object.Kuksa_Signals["CM_brake"][1] = self.Car_Maker_Object.CM_Signals["brake"][1]

            self.Digital_Auto_Object.Kuksa_Signals["CM_vehspeed"][1] = (self.Car_Maker_Object.CM_Signals["vehspd"][1])

            self.Digital_Auto_Object.Kuksa_Signals["CM_acttrq"][1] = (self.Car_Maker_Object.CM_Signals["acttrq"][1])
            
            self.Digital_Auto_Object.Kuksa_Signals["CM_destrq"][1] = (self.Car_Maker_Object.CM_Signals["destrq"][1])
                      
            
            self.Digital_Auto_Object.Kuksa_Signals["CM_beakepr"][1] = (self.Car_Maker_Object.CM_Signals["brakepr"][1])
            
            self.Digital_Auto_Object.Kuksa_Signals["CM_braketrq"][1] = (self.Car_Maker_Object.CM_Signals["braketrq"][1])

            time.sleep(0.1)

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    try:
        Execute_Demo = DemoController()
    except Exception as e:
        print(f"An error occurred: {e}")
