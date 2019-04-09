from components import *


def control_system(state, dt):
    for control_cmp in state.get_components_by_class(ControlComponent):
        position_cmp = control_cmp.parent.get_first_component_by_class(PositionComponent)
        kinematic_cmp = control_cmp.parent.get_first_component_by_class(KinematicComponent)
        kinematic_cmp.speed += control_cmp.acc * dt
        position_cmp.pos += kinematic_cmp.speed * dt
        position_cmp.rot += 1