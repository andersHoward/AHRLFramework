from game_ecs import GameSystem
import Constants as CONST

class SYS_AbilityHandler(GameSystem):
    def __init__(self):
        super(self)

    def set_up_spell(self, spell_param_dict ):
        #TODO maybe switch to an enum class instead of a dict here.
        _spell_name = spell_param_dict['spell_name']
        _spell_target_style = spell_param_dict['spell_target_style']
        _spell_target = self.get_spell_target()
        _spell_value_attr_type = spell_param_dict['spell_value_attr_type']
        _spell_value = spell_param_dict['spell_value']
        _spell_class = spell_param_dict['spell_class']
        _spell_success_message = spell_param_dict['spell_message']
        _spell_fail_message = spell_param_dict['spell_fail_message']
        _spell_persistent_effect = spell_param_dict['spell_persistent_effect']

    def get_spell_target(self):
        if self._spell_target_style == CONST.E_SPELL_TARGET_STYLE.user_selected_npc:
            #TODO ask UI for user input.
            pass
        elif self._spell_target_style == CONST.E_SPELL_TARGET_STYLE.user_selected_location:
            #TODO ask ui for input
            pass
        elif self.get_spell_target_style == CONST.E_SPELL_TARGET_STYLE.entity_origin_burst:
            #TODO enttity origin burst
            pass

    def cast_spell(self):
        pass

