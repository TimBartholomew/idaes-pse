##############################################################################
# Institute for the Design of Advanced Energy Systems Process Systems
# Engineering Framework (IDAES PSE Framework) Copyright (c) 2018-2019, by the
# software owners: The Regents of the University of California, through
# Lawrence Berkeley National Laboratory,  National Technology & Engineering
# Solutions of Sandia, LLC, Carnegie Mellon University, West Virginia
# University Research Corporation, et al. All rights reserved.
#
# Please see the files COPYRIGHT.txt and LICENSE.txt for full copyright and
# license information, respectively. Both files are also available online
# at the URL "https://github.com/IDAES/idaes-pse".
##############################################################################
"""
Tests for ideal state block; only tests for construction
Author: Jaffer Ghouse
"""
import pytest
from pyomo.environ import ConcreteModel

from idaes.core import FlowsheetBlock
from idaes.property_models.ideal.BTX_ideal_VLE import IdealParameterBlock
from idaes.ui.report import degrees_of_freedom

# -----------------------------------------------------------------------------
m = ConcreteModel()
# Create a flowsheet object to test inlet state blocks
m.fs = FlowsheetBlock(default={"dynamic": False})

# vapor-liquid
m.fs.properties_vl = IdealParameterBlock(default={"valid_phase":
                                                  ('Liq', 'Vap')})
m.fs.state_block_vl = m.fs.properties_vl.state_block_class(
    default={"parameters": m.fs.properties_vl,
             "defined_state": True})

# liquid only
m.fs.properties_l = IdealParameterBlock(default={"valid_phase": 'Liq'})
m.fs.state_block_l = m.fs.properties_l.state_block_class(
    default={"parameters": m.fs.properties_l,
             "has_phase_equilibrium": False,
             "defined_state": True})

# vapor only
m.fs.properties_v = IdealParameterBlock(default={"valid_phase": 'Vap'})
m.fs.state_block_v = m.fs.properties_v.state_block_class(
    default={"parameters": m.fs.properties_v,
             "has_phase_equilibrium": False,
             "defined_state": True})


def test_build_inlet_state_blocks():
    assert len(m.fs.properties_vl.config) == 2

    # vapor-liquid
    assert m.fs.properties_vl.config.valid_phase == ('Vap', 'Liq') or \
        m.fs.properties_vl.config.valid_phase == ('Liq', 'Vap')
    assert len(m.fs.properties_vl.phase_list) == 2
    assert m.fs.properties_vl.phase_list == ["Liq", "Vap"]
    assert hasattr(m.fs.state_block_vl, "eq_Keq")
    assert not hasattr(m.fs.state_block_vl, "eq_mol_frac_out")

    # liquid only
    assert m.fs.properties_l.config.valid_phase == "Liq"
    assert len(m.fs.properties_l.phase_list) == 1
    assert m.fs.properties_l.phase_list == ["Liq"]
    assert not hasattr(m.fs.state_block_l, "eq_Keq")
    assert not hasattr(m.fs.state_block_vl, "eq_h_vap")
    assert not hasattr(m.fs.state_block_l, "eq_mol_frac_out")

    # vapor only
    assert m.fs.properties_v.config.valid_phase == "Vap"
    assert len(m.fs.properties_v.phase_list) == 1
    assert m.fs.properties_v.phase_list == ["Vap"]
    assert not hasattr(m.fs.state_block_v, "eq_Keq")
    assert not hasattr(m.fs.state_block_vl, "eq_h_liq")
    assert not hasattr(m.fs.state_block_v, "eq_mol_frac_out")


def test_setInputs_inlet_state_blocks():

    # vapor-liquid
    m.fs.state_block_vl.flow_mol.fix(1)
    m.fs.state_block_vl.temperature.fix(368)
    m.fs.state_block_vl.pressure.fix(101325)
    m.fs.state_block_vl.mole_frac["benzene"].fix(0.5)
    m.fs.state_block_vl.mole_frac["toluene"].fix(0.5)

    assert degrees_of_freedom(m.fs.state_block_vl) == 0

    # liquid only
    m.fs.state_block_l.flow_mol.fix(1)
    m.fs.state_block_l.temperature.fix(362)
    m.fs.state_block_l.pressure.fix(101325)
    m.fs.state_block_l.mole_frac["benzene"].fix(0.5)
    m.fs.state_block_l.mole_frac["toluene"].fix(0.5)

    assert degrees_of_freedom(m.fs.state_block_l) == 0

    # vapor only
    m.fs.state_block_v.flow_mol.fix(1)
    m.fs.state_block_v.temperature.fix(375)
    m.fs.state_block_v.pressure.fix(101325)
    m.fs.state_block_v.mole_frac["benzene"].fix(0.5)
    m.fs.state_block_v.mole_frac["toluene"].fix(0.5)

    assert degrees_of_freedom(m.fs.state_block_v) == 0


def test_bubbleT_inlet_state_blocks():
    assert m.fs.state_block_vl.temperature_bubble_point(
        101325, m.fs.state_block_vl.mole_frac,
        options={"initial_guess": 298.15,
                 "tol": 1e-3,
                 "deltaT": 1e-2,
                 "max_iter": 1e4}) == \
        pytest.approx(365.314, abs=1e-2)


def test_dewT_inlet_state_blocks():
    assert m.fs.state_block_vl.temperature_dew_point(
        101325, m.fs.state_block_vl.mole_frac,
        options={"initial_guess": 298.15,
                 "tol": 1e-3,
                 "deltaT": 1e-2,
                 "max_iter": 1e4}) == \
        pytest.approx(371.987, abs=1e-2)


def test_bubbleP_inlet_state_blocks():
    assert m.fs.state_block_vl.pressure_bubble_point(
        365.314, m.fs.state_block_vl.mole_frac) == \
        pytest.approx(101325, abs=1e-1)


def test_dewP_inlet_state_():
    assert m.fs.state_block_vl.pressure_dew_point(
        371.987, m.fs.state_block_vl.mole_frac) == \
        pytest.approx(101325, abs=1e-1)


# Create a flowsheet object to test outlet state blocks
m.fs1 = FlowsheetBlock(default={"dynamic": False})
# vapor-liquid
m.fs1.properties_vl = IdealParameterBlock(default={"valid_phase":
                                                   ('Liq', 'Vap')})
m.fs1.state_block_vl = m.fs1.properties_vl.state_block_class(
    default={"parameters": m.fs1.properties_vl,
             "defined_state": False})

# liquid only
m.fs1.properties_l = IdealParameterBlock(default={"valid_phase": 'Liq'})
m.fs1.state_block_l = m.fs1.properties_l.state_block_class(
    default={"parameters": m.fs1.properties_l,
             "has_phase_equilibrium": False,
             "defined_state": False})

# vapor only
m.fs1.properties_v = IdealParameterBlock(default={"valid_phase": 'Vap'})
m.fs1.state_block_v = m.fs1.properties_v.state_block_class(
    default={"parameters": m.fs1.properties_v,
             "has_phase_equilibrium": False,
             "defined_state": False})


def test_build_outlet_state_blocks():
    assert len(m.fs1.properties_vl.config) == 2

    # vapor-liquid
    assert m.fs1.properties_vl.config.valid_phase == ('Vap', 'Liq') or \
        m.fs1.properties_vl.config.valid_phase == ('Liq', 'Vap')
    assert len(m.fs1.properties_vl.phase_list) == 2
    assert m.fs1.properties_vl.phase_list == ["Liq", "Vap"]
    assert hasattr(m.fs1.state_block_vl, "eq_Keq")
    assert hasattr(m.fs1.state_block_vl, "eq_mol_frac_out")

    # liquid only
    assert m.fs1.properties_l.config.valid_phase == "Liq"
    assert len(m.fs1.properties_l.phase_list) == 1
    assert m.fs1.properties_l.phase_list == ["Liq"]
    assert not hasattr(m.fs1.state_block_l, "eq_Keq")
    assert not hasattr(m.fs1.state_block_vl, "eq_h_vap")
    assert hasattr(m.fs1.state_block_l, "eq_mol_frac_out")

    # vapor only
    assert m.fs1.properties_v.config.valid_phase == "Vap"
    assert len(m.fs1.properties_v.phase_list) == 1
    assert m.fs1.properties_v.phase_list == ["Vap"]
    assert not hasattr(m.fs1.state_block_v, "eq_Keq")
    assert not hasattr(m.fs1.state_block_vl, "eq_h_liq")
    assert hasattr(m.fs1.state_block_v, "eq_mol_frac_out")


def test_setInputs_outlet_state_blocks():

    # vapor-liquid
    m.fs1.state_block_vl.flow_mol.fix(1)
    m.fs1.state_block_vl.temperature.fix(368)
    m.fs1.state_block_vl.pressure.fix(101325)
    m.fs1.state_block_vl.mole_frac["benzene"].fix(0.5)

    assert degrees_of_freedom(m.fs.state_block_vl) == 0

    # liquid only
    m.fs1.state_block_l.flow_mol.fix(1)
    m.fs1.state_block_l.temperature.fix(362)
    m.fs1.state_block_l.pressure.fix(101325)
    m.fs1.state_block_l.mole_frac["benzene"].fix(0.5)

    assert degrees_of_freedom(m.fs.state_block_l) == 0

    # vapor only
    m.fs1.state_block_v.flow_mol.fix(1)
    m.fs1.state_block_v.temperature.fix(375)
    m.fs1.state_block_v.pressure.fix(101325)
    m.fs1.state_block_v.mole_frac["benzene"].fix(0.5)

    assert degrees_of_freedom(m.fs.state_block_v) == 0
