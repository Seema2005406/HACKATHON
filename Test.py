import logging
from types import *
import time
import threading
from pycarmaker import CarMaker, Quantity  # CarMaker Library
from kuksa_client.grpc import VSSClient, Datapoint  # Kuksa Library

# Helper functions to emulate unsigned integer types
def uint8(value):
    if not (0 <= value <= 255):
        raise ValueError(f"Value {value} out of range for uint8 (0-255)")
    return int(value)

def uint16(value):
    if not (0 <= value <= 65535):
        raise ValueError(f"Value {value} out of range for uint16 (0-65535)")
    return int(value)

def uint32(value):
    if not (0 <= value <= 4294967295):
        raise ValueError(f"Value {value} out of range for uint32 (0-4294967295)")
    return int(value)

def int16(value):
    if not (-32768 <= value <= 32767):
        raise ValueError(f"Value {value} out of range for int16 (-32768 to 32767)")
    return int(value)

# Global variables
digitalAuto_Gas = 0
digitalAuto_Brake = 0
digitalAuto_Speed = 0
digitalAuto_TorqueEff = 0
digitalAuto_TorqueDes = 0
digitalAuto_TorqueRL = 0
digitalAuto_TorqueRR = 0
digitalAuto_Hyssyspmc = 0

# Function Definitions
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

    cm.subscribe(vehspd)
    cm.subscribe(brake)
    cm.subscribe(gas)
    cm.subscribe(tqeff)
    cm.subscribe(tqdis)
    cm.subscribe(tqrl)
    cm.subscribe(tqrr)
    cm.subscribe(hydsyspmc)

    print(cm.send("StartSim\r"))
    print(cm.send("WaitForStatus running\r"))

    while True:
        cm.read()

        # Update vehicle data
        digitalAuto_Speed = vehspd.data * 3.6
        print("Vehicle speed: " + str(digitalAuto_Speed) + "(km/h)")

        digitalAuto_Gas = gas.data
        print("Vehicle gas: " + str(digitalAuto_Gas))

        # Brake condition
        digitalAuto_Brake = brake.data
        print("Vehicle Brake: " + str(digitalAuto_Brake))

        digitalAuto_TorqueEff = tqeff.data
        print("Vehicle tq eff: " + str(digitalAuto_TorqueEff))

        digitalAuto_TorqueDes = tqdis.data
        print("Vehicle tq des: " + str(digitalAuto_TorqueDes))

        digitalAuto_TorqueRL = tqrl.data
        print("Vehicle tq rl: " + str(digitalAuto_TorqueRL))

        digitalAuto_TorqueRR = tqrr.data
        print("Vehicle tq rr: " + str(digitalAuto_TorqueRR))

        digitalAuto_Hyssyspmc = hydsyspmc.data
        print("Vehicle hyd sys pmc: " + str(digitalAuto_Hyssyspmc))

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

    kuksaDataBroker_IP = "localhost"
    kuksaDataBroker_Port = 55555

    with VSSClient(kuksaDataBroker_IP, kuksaDataBroker_Port) as client:
        while True:
            # Update vehicle speed and brake status to the Kuksa client
            client.set_current_values({'Vehicle.Speed': Datapoint(float(digitalAuto_Speed))})
            print("Digital Vehicle Speed: " + str(digitalAuto_Speed))

            client.set_current_values({'Vehicle.Chassis.Accelerator.PedalPosition': Datapoint(uint8(digitalAuto_Gas))})
            print("Digital gas: " + str(digitalAuto_Gas))

            client.set_current_values({'Vehicle.Powertrain.ElectricMotor.Torque': Datapoint(int16(digitalAuto_TorqueEff))})
            print("Digital tq eff: " + str(digitalAuto_TorqueEff))

            client.set_current_values({'Vehicle.Powertrain.ElectricMotor.TimeInUse': Datapoint(uint32(digitalAuto_TorqueDes))})
            print("Digital tq des: " + str(digitalAuto_TorqueDes))

            client.set_current_values({'Vehicle.Chassis.Axle.Row1.Wheel.Left.Brake.FluidLevel': Datapoint(uint8(digitalAuto_Hyssyspmc))})
            print("Digital tq hyd sys pmc: " + str(digitalAuto_Hyssyspmc))

            client.set_current_values({'Vehicle.Chassis.Axle.Row1.Wheel.Left.Tire.Pressure': Datapoint(uint8(digitalAuto_TorqueRL))})
            print("Digital tq rl: " + str(digitalAuto_TorqueRL))

            client.set_current_values({'Vehicle.Chassis.Axle.Row1.Wheel.Right.Tire.Pressure': Datapoint(uint8(digitalAuto_TorqueRR))})
            print("Digital tq rr: " + str(digitalAuto_TorqueRR))

            client.set_current_values({'Vehicle.Chassis.Brake.PedalPosition': Datapoint(uint8(digitalAuto_Brake))})
            print("Digital brake position: " + str(digitalAuto_Brake))

            time.sleep(1)

# Main Execution
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
