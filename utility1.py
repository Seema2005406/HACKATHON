import logging
from types import *
import time
from pycarmaker import CarMaker, Quantity #Python CarMaker Library
from kuksa_client.grpc import VSSClient #Kuksa Library
from kuksa_client.grpc import Datapoint #Kuksa Library
from enum import Enum
import subprocess

class MyCarMaker:
    
    class State(Enum):
        Stop    = 0
        Initial = 1
        Running = 2
    
    def __init__(self):
        self.CM_State       = self.State.Stop.value
        self.CM_IP          = "localhost"
        self.CM_Port        = 16660 
        self.CM             = CarMaker(self.CM_IP, self.CM_Port)
        self.CM_Path        = r"C:\IPG\carmaker\win64-13.1\bin\CM_Office.exe"
        self.CM_TestRun     = "C:\CM_Projects\team1\Data\TestRun\SampleTestRun"
        self.CM_Linux       = "cd /opt/ipg/bin && vglrun -d :0 ./CM_Office -cmdport 16660"
        self.Linux_TestRun  = "/home/eurus01/Desktop/Dev/eurusCarMakerDemo/Data/TestRun/EurusDemoTestRun"
        self.CM_Signals     = {
        #   Key_Name       Subcriber_Name                                  Signal_Value   Signal_Type
            "gas"      : [Quantity("DM.Gas", Quantity.FLOAT)  ,  0            , "Input"   ],
            "brake"       : [Quantity("DM.Brake", Quantity.FLOAT)    ,  0            , "Input"    ],
            "vehspd"    : [Quantity("FMU.SWAN_Vco.In.Bdy_vVeh", Quantity.FLOAT)            ,  0            , "Input"    ],
            "acttrq"  : [Quantity("FMU.SWAN_Vco.In.Ema_tqEffEma", Quantity.FLOAT) ,  0            , "Input"    ],
            "destrq"    : [Quantity("FMU.SWAN_Vco.Out.Vco_tqDesEdr", Quantity.FLOAT)        ,  0            , "Input"    ],
            "brakepr"     : [Quantity("Brake.Hyd.Sys.pMC", Quantity.FLOAT)         ,  0            , "Input"   ] 
            "braketrq"     : [Quantity("Brake.Trq_WB_RL", Quantity.FLOAT)         ,  0            , "Input"   ]             
        }

    def Open_In_Windows(self):
        # Change the state to Initial
        self.CM_State = self.State.Initial.value
        print("Open Car Maker Application")
        exe_path = self.CM_Path
        #command = [exe_path, f"-cmdport 16660"]
        #process = subprocess.Popen(exe_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        parameters = ["-cmdport", "16660"]
        subprocess.Popen([exe_path] + parameters)
        #subprocess.run([exe_path, f"-cmdport 16660"])
        time.sleep(10)

    def Open_In_Linux(self):
        # Change the state to Initial
        self.CM_State = self.State.Initial.value
        
        print("Open Car Maker Application")
        subprocess.Popen(self.CM_Linux, shell=True)
        time.sleep(5)

    def Connect(self):
        self.CM.connect()
        print("Car Maker Connected")
        time.sleep(0.5)
        
    def Load_Test_Run(self):
        print(self.CM.send("LoadTestRun C:/CM_Projects/team1/Data/TestRun/SampleTestRun\r"))
        print("Test run loaded")
        time.sleep(0.5)

    def Start_Simulation(self):
        print("\r++++++++++++++++++++++++++++++\r")
        print(" Welcome to BCU Demonstration\r")
        print("++++++++++++++++++++++++++++++++\r")

        print(self.CM.send("StartSim\r"))
        print(self.CM.send("WaitForStatus running\r"))
        time.sleep(1) # Keep time.sleep(1) here to run the car

        # Change the state to Running
        self.CM_State = self.State.Running.value
        
    def Stop_Simulation(self):
        print("++++++++++++++++++++++++++++++++\r")
        print(" BCU Demonstration is finished\r")
        print("++++++++++++++++++++++++++++++++\r\n")
        print(self.CM.send("StopSim\r"))
        time.sleep(0.5)

    def Get_Signal(self):
        for key in self.CM_Signals:
            if self.CM_Signals[key][2] == "Input":
                self.CM.subscribe(self.CM_Signals[key][0])
                time.sleep(0.1)
        self.CM.read()

    def Set_Signal(self):
        for key in self.CM_Signals:
            if self.CM_Signals[key][2] == "Output":
                self.CM.DVA_write(self.CM_Signals[key][0], self.CM_Signals[key][1])
                time.sleep(0.1)
        
    def Close(self):
        print(self.CM.send("GUI quit\r"))
        print("GUI Quit")
        time.sleep(1)
        #print(self.CM.send("Application shutdown\r"))
        print("Application Shutdown")
        #time.sleep(1)
        print("Close CarMaker")
        # Change the state to Stop
        self.CM_State = self.State.Stop.value
        
class MyDockerDigitalAuto:

    def __init__(self):
        self.Kuksa_DB_IP = 'localhost'
        self.Kuksa_DB_Port = 55555
        self.Kuksa_Signals = {
        #   Key_Name          Kuksa_Signal_Name                                                 Signal_Value   Signal_Type
            "CM_gas"    : ["Vehicle.Chassis.Accelerator.PedalPosition", 0       , "Output"    ],
            "CM_brake"     : ["Vehicle.Chassis.Brake.PedalPosition"                             , 0           , "Output"   ],
            "CM_vehspd"          : ["Vehicle.Speed"      , 0         , "Output"   ],
            "CM_acttrq"  : ["VVehicle.Powertrain.ElectricMotor.Torque"                       , 0       , "Output"   ],
            "CM_destrq"   : ["Vehicle.Powertrain.ElectricMotor.TimeInUse"                           , 0      , "Output"   ],
            "CM_brakepr"   : ["Vehicle.Chassis.Axle.Row1.Wheel.Left.Brake.FluidLevel"                           , 0      , "Output"   ],
            "CM_braketrq"   : ["Vehicle.Chassis.Axle.Row1.Wheel.Left.Tire.Pressure"                           , 0      , "Output"   ]
        }
        self.Kuksa_client = VSSClient(self.Kuksa_DB_IP, self.Kuksa_DB_Port)
        self.Kuksa_client.connect()
        self.Set_Signal()

    def Get_Signal(self):
        print(f"- Getting Kuksa Signal ...")
        for key in self.Kuksa_Signals:
            if self.Kuksa_Signals[key][2] == "Input":
                target_value = self.Kuksa_client.get_target_values([self.Kuksa_Signals[key][0],])
                self.Kuksa_Signals[key][1] = target_value[self.Kuksa_Signals[key][0]].value
                # print(f"- Getting: {self.Kuksa_Signals[key][0]} = {self.Kuksa_Signals[key][1]}")
                self.Kuksa_client.set_current_values({self.Kuksa_Signals[key][0]:Datapoint(target_value[self.Kuksa_Signals[key][0]].value),})
                
    def Set_Signal(self):
        print(f"- Setting Kuksa Signal ...")
        for key in self.Kuksa_Signals:
            self.Kuksa_client.set_current_values({self.Kuksa_Signals[key][0]:Datapoint(self.Kuksa_Signals[key][1]),})
            if key != "temp":
                self.Kuksa_client.set_target_values({self.Kuksa_Signals[key][0]:Datapoint(self.Kuksa_Signals[key][1]),})
                # print(f"- Setting: {self.Kuksa_Signals[key][0]}")
