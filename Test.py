import logging
from types import *
import time
import threading
from pycarmaker import CarMaker, Quantity  # CarMaker Library
from kuksa_client.grpc import VSSClient, Datapoint  # Kuksa Library

print("\r++++++++++++++++++++++++++++++++++++\r")
print("Welcome to Demon 3 in Windows Server\r")
print("+++++++++++++++++++++++++++++++++++++\r")

# Global variables
digitalAuto_Gas = 0
digitalAuto_Brake = 0
digitalAuto_Speed = 0
digitalAuto_TorqueEff =0
digitalAuto_TorqueDes = 0
digitalAuto_TorqueRL= 0
digitalAuto_TorqueRR = 0
digitalAuto_Hyssyspmc = 0



def thread_ControlCarMaker():
    global digitalAuto_Gas
    global digitalAuto_Brake
    global digitalAuto_Speed
    global digitalAuto_TorqueEff
    global digitalAuto_TorqueDes
    global digitalAuto_TorqueRL
    global digitalAuto_TorqueRR
    global digitalAuto_Hyssyspmc

    carMaker_IP = "localhost"
    carMaker_Port = 16660

    cm = CarMaker(carMaker_IP, carMaker_Port)
    cm.connect()

    vehspd = Quantity("FMU.SWAN_Vco.In.Bdy_vVeh", Quantity.FLOAT)
    brake = Quantity("DM.Brake", Quantity.FLOAT)
    gas = Quantity("DM.Gas", Quantity.FLOAT)
    tqeff = Quantity("FMU.SWAN_Vco.In.Bdy_vVeh", Quantity.FLOAT)
    tqdis = Quantity("FMU.SWAN_Vco.Out.Vco_tqDesEdr", Quantity.FLOAT)
    tqrl = Quantity("Brake.Trq_WB_RL", Quantity.FLOAT)
    tqrr = Quantity("Brake.Trq_WB_RR", Quantity.FLOAT)
    hydsyspmc = Quantity("Brake.Hyd.Sys.pMC", Quantity.FLOAT)

    print(cm.send("StartSim\r"))
    print(cm.send("WaitForStatus running\r"))

    while True:
        cm.read()

        # Update vehicle data
        digitalAuto_Speed = vehspd.data * 3.6
        print("Vehicle speed: " + str(digitalAuto_Speed) + "(km/h)")

        digitalAuto_Gas  = gas.data
        print("Vehicle gas: " + str(digitalAuto_Hazard))

        # Brake condition
        digitalAuto_Brake = brake.data
        print("Vehicle Brake: " + str(digitalAuto_Brake))

        digitalAuto_TorqueEff = tqeff.data
        print("Vehicle tq eff: " + str(digitalAuto_TorqueEff) + "(km/h)")

        digitalAuto_TorqueDes  = tqdis.data
        print("Vehicle tq des: " + str(digitalAuto_TorqueDes))

        # Brake condition
        digitalAuto_TorqueRL = tqrl.data
        print("Vehicle tq rl: " + str(digitalAuto_TorqueRL))

        digitalAuto_TorqueRR  = tqrr.data
        print("Vehicle tq rr: " + str(digitalAuto_TorqueRR))

        # Brake condition
        digitalAuto_Hyssyspmc = hydsyspmc.data
        print("Vehicle hyd sys pmc: " + str(digitalAuto_Hyssyspmc))

        # Toggle mechanism for user input (userinput.data == 1)
        # Update the last user input
        time.sleep(1)

def thread_ConnectToDigitalAuto():
    global digitalAuto_Gas
    global digitalAuto_Brake
    global digitalAuto_Speed
    global digitalAuto_TorqueEff
    global digitalAuto_TorqueDes
    global digitalAuto_TorqueRL
    global digitalAuto_TorqueRR
    global digitalAuto_Hyssyspmc

    carMaker_IP = "localhost"
    carMaker_Port = 16660
    cm = CarMaker(carMaker_IP, carMaker_Port)
    cm.connect()

    kuksaDataBroker_IP = "localhost"
    kuksaDataBroker_Port = 55555


    with VSSClient(kuksaDataBroker_IP, kuksaDataBroker_Port) as client:
        while True:
            # Exit the loop to continue the main flow

            # Update vehicle speed and brake status to the Kuksa client
            client.set_current_values({'Vehicle.Speed': Datapoint(float(digitalAuto_Speed))})
            print("Digital Vehicle Speed: " + str(digitalAuto_Speed))

            client.set_current_values({'Vehicle.Chassis.Accelerator.PedalPosition': Datapoint(float(digitalAuto_Gas))})
            print("Digital gas: " + str(digitalAuto_Gas))

            client.set_current_values({'Vehicle.Powertrain.ElectricMotor.Torque': Datapoint(float(digitalAuto_TorqueEff))})
            print("Digital tq eff: " + str(digitalAuto_TorqueEff))

            client.set_current_values({'Vehicle.Powertrain.ElectricMotor.TimeInUse': Datapoint(float(digitalAuto_TorqueDes))})
            print("Digital tq des: " + str(digitalAuto_TorqueDes))

            client.set_current_values({'Vehicle.Chassis.Axle.Row1.Wheel.Left.Brake.FluidLevel': Datapoint(float(digitalAuto_Hyssyspmc))})
            print("Digital tq hyd sys pmc: " + str(digitalAuto_Hyssyspmc))

            client.set_current_values({'Vehicle.Chassis.Axle.Row1.Wheel.Left.Tire.Pressure': Datapoint(float(digitalAuto_TorqueRL))})
            print("Digital tq rl: " + str(digitalAuto_TorqueRL))

            client.set_current_values({'Vehicle.Chassis.Axle.Row1.Wheel.Right.Tire.Pressure': Datapoint(float(digitalAuto_TorqueRR))})
            print("Digital tq rr: " + str(digitalAuto_TorqueRR))

            client.set_current_values({'Vehicle.Chassis.Brake.PedalPosition': Datapoint(float(digitalAuto_Brake))})
            print("Digital tq rr: " + str(digitalAuto_Brake))


            time.sleep(1)

if __name__ == '__main__':
    try:
        # Declare threads
        CarMakerThread = threading.Thread(target=thread_ControlCarMaker)
        DigitalAutoThread = threading.Thread(target=thread_ConnectToDigitalAuto)

        # Start threads
        CarMakerThread.start()
        DigitalAutoThread.start()

        # Wait for threads to finish
        CarMakerThread.join()
        DigitalAutoThread.join()

        print("+++++++++++++++++++++++++++\r")
        print("Demonstration is finished\r")
        print("+++++++++++++++++++++++++++\r\n")

    except Exception as e:
        print(f"Something went wrong: {e}")
