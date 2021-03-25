# Elaine Laguerta (github: @elaguerta)
# LBNL GIG
# File created: 19 February 2021
# Create Solution superclass

from circuit import Circuit
from volt_var_controller import VoltVARController
import utils
import opendssdirect as dss

import re
import numpy as np


class Solution():

    # class variables set for all SolutionNR3 instances
    # TODO: If any of these need to be set by instance, move into self.__init__
    SLACKIDX = 0  # assume slack bus is at index 0
    VSLACK = np.array([1, np.exp(1j*-120*np.pi/180), np.exp(1j*120*np.pi/180)])
    V0, I0 = None, None
    tolerance = 1e-9
    maxiter = 100
    ZIP_V = [0.10, 0.05, 0.85, 0.10, 0.05, 0.85, 0.80]

    def __init__(self, dss_fp: str):
        """
        sets up a Solution object with a pointer to a Circuit mapped from opendss
        Solutions keep a pointer to the dss object used to map the Circuit
        """
        self.dss = dss.run_command('Redirect ' + dss_fp)
        dss.Solution.Solve()  # solve first for base values
        utils.set_zip_values(dss, self.__class__.ZIP_V)  # set zip values before mapping Circuit!
        dss.Solution.Solve()  # solve again to set zip values
        self.circuit = Circuit(dss)
        self.volt_var_controllers = self.parse_vvc_objects(dss_fp)

    def parse_vvc_objects(self, fn: str):
        """ From 20180601/PYTHON/lib/dss_vvc.py by @kathleenchang"""
        # Parse VVC lines in DSS file
        vvarobjects = []
        f = open(fn, "r")

        for l in f:
            if re.findall('(?i)New VVC', l):
                bp = []

                #array of VVC breakpoints
                breakpoints = str.split(re.findall(r"(?i)BP=\s*([^\n\r]*)", l)[0], ',')

                for elem in breakpoints:
                    point = re.findall("[0-9.]*",  elem)
                    for i in point:
                        if i:
                            bp.append(float(i))
                print(bp)

                # zero-indexed phase, is one-indexed in DSS file
                phase = int(re.findall('(?i)phase=\s*([0-9]*)', l)[0]) - 1
                print(phase)

                minkvar = float(re.findall('(?i)min_kvar=([-0-9]*)', l)[0])
                print(minkvar)

                maxkvar = float(re.findall('(?i)max_kvar=([-0-9]*)', l)[0])
                print(maxkvar)

                bus = re.findall(r"(?i)bus=([\w.]*)\s", l)[0]
                bus = re.findall(r"[\w]*", bus)[0]
                print(bus)

                # create volt var object
                voltvarobject = VoltVARController(bp, minkvar, maxkvar, bus, phase)
                vvarobjects.append(voltvarobject)
                print("\n --------------")

        for e in vvarobjects:
            print(e)
        return vvarobjects
    
    def volt_var_control(self):
        print('hi')
    
    def regulator_ldc_control(self):
        nnode = self.circuit.buses.num_elements
        nline = self.circuit.lines.num_elements
        vr_lines = self.circuit.voltage_regulators.get_num_lines_x_ph
        tf_lines = self.circuit.transformers.get_num_lines_x_ph
        XNR = self.XNR
        
        vr_idx_dict = voltage_regulator_index_dict() 
        vr_line_idx = range(0, vr_lines)
        
    
        # flag if need to rerun NR3
        flag = 0
        vr_line_counter = 0
        XNR_final = XNR
    
        for k in vr_idx_dict.keys():
            for vridx in vr_idx_dict[k]: #{bus: [indices in dss.RegControls.AllNames(), ...]}
                
                dss.RegControls.Name(dss.RegControls.AllNames()[vridx])
                dss.Circuit.SetActiveBus(dss.CktElement.BusNames()[0].split(".")[0])
                winding = dss.RegControls.Winding()
            
                Vbase = dss.Bus.kVBase() *1000
                Sbase = 10**6
                Ibase = Sbase / Vbase
                band = dss.RegControls.ForwardBand()
                target_voltage = dss.RegControls.ForwardVreg()

                idxbs = dss.Circuit.AllBusNames().index((dss.CktElement.BusNames()[0].split('.')[0]))   
            
                ph = dss.CktElement.BusNames()[0].split('.')[1:] 
                ph_arr = [0, 0, 0]
                for i in ph:
                    ph_arr[int(i) - 1] = 1
                if len(ph) == 0:
                    ph_arr = [1, 1, 1]
                for ph in range(len(ph_arr)):
                    if ph_arr[ph] == 1: #loop over existing phases of voltage regulator
                        
                        NR_voltage = np.abs((XNR[2*nnode*ph + 2*idxbs]  + (1j * XNR[2*nnode*ph + 2*idxbs + 1])) * Vbase / dss.RegControls.PTRatio())

                        if dss.RegControls.ForwardR() and dss.RegControls.ForwardX() and dss.RegControls.CTPrimary():
                            # if LDC exists

                            #vr_line_counter - counts the number of lines passed; two lines for every phase
                            #vridx - index of current voltage regulator in dss.RegControls.AllNames()
                            #tf_lines - number of transformers
                            
                            line_idx =  2*vr_line_idx[vr_line_counter] + 2*(winding - 1)

                            I_reg = XNR[2*3*(nnode+nline) + 2*tf_lines + line_idx] + \
                                1j * XNR[2*3*(nnode+nline) + 2*tf_lines +  line_idx + 1]

                            V_drop = (dss.RegControls.ForwardR() + 1j*dss.RegControls.ForwardX()) / 0.2 * (I_reg * Ibase / dss.RegControls.CTPrimary())     
                        
                            V_drop = (dss.RegControls.ForwardR() + 1j*dss.RegControls.ForwardX()) / 0.2 * (I_reg * Ibase / (dss.RegControls.CTPrimary()/0.2))
                            V_R = np.abs(NR_voltage - V_drop)

                            abs_diff = np.abs(V_R - target_voltage)
                            V_compare = V_R
                            print('vcompare', dss.RegControls.Name(), V_compare)
                                    
                        else:
                            # if LDC term does not exist
                            print('**** LDC missing term ***** ')
                            abs_diff = np.abs(NR_voltage - target_voltage)
                            V_compare = NR_voltage
    
                        print('absolute difference: ', abs_diff, "\n")
                        vr_line_counter += 1
                    
                        # compare NR3 voltage to forward Vreg voltage +- band
                        if abs_diff <= band: #converges
                            XNR_final = XNR
                            continue
                                
                        elif abs_diff > band:
                            if V_compare > (target_voltage + band): #NR3 voltage above forward-Vreg
                                if dss.RegControls.TapNumber() <= -16 :
                                    print('Tap Number Out of Bounds' )
                                    XNR_final = XNR
                            
                                else:
                                    print('Decrease Tap Number')
                                    dss.RegControls.TapNumber(dss.RegControls.TapNumber() - 1)
                                    print('New tap number ', dss.RegControls.TapNumber())
                                    flag = 1 #run NR3 again
                            else: #NR3 voltage below forward-Vreg
                                if dss.RegControls.TapNumber() >= 16:
                                    print('Tap Number Out of Bounds' )
                                    print('New tap number ', dss.RegControls.TapNumber())
                                    XNR_final = XNR
                            
                                else:
                                    print('Increase tap number')
                                    dss.RegControls.TapNumber(dss.RegControls.TapNumber() + 1)
                                    flag = 1 #run NR3 again
            if flag == 1:
                return flag, XNR_final
        return flag, XNR_final