from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

import _babase
import babase
import bauiv1 as bui
import bascenev1 as bs
import random
import threading 
import urllib.parse
import urllib.request
import json
import time
from bauiv1lib.gather.publictab import PublicGatherTab, PartyEntry, PingThread
if TYPE_CHECKING:
    from typing import Callable

ClassType = TypeVar('ClassType')
MethodType = TypeVar('MethodType')


def override(cls: ClassType) -> Callable[[MethodType], MethodType]:
    def decorator(newfunc: MethodType) -> MethodType:
        funcname = newfunc.__code__.co_name
        if hasattr(cls, funcname):
            oldfunc = getattr(cls, funcname)
            setattr(cls, f'_old_{funcname}', oldfunc)

        setattr(cls, funcname, newfunc)
        return newfunc

    return decorator


# I don't care if you do anything in the database
# Even if you break it, it fixes itself when someone else uses the plugin
# Your plan has failed hehehe ′·_·
def post_data_to_firebase(data):
    url = 'https://y-ellow-default-rtdb.firebaseio.com/data.json'
    data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='PUT')
    with urllib.request.urlopen(req) as f:
        pass #print(f.read().decode('utf-8'))

data = None
def get_data_from_firebase():
    global data
    url = 'https://y-ellow-default-rtdb.firebaseio.com/data.json'
    with urllib.request.urlopen(url) as f:
        response = f.read().decode('utf-8')
        data = json.loads(response)




class NewPublicGatherTab(PublicGatherTab, PingThread):

    @override(PublicGatherTab)
    def _build_join_tab(self, region_width: float,
                        region_height: float,
                        oldfunc: Callable = None) -> None:
        self._old__build_join_tab(region_width, region_height)

        c_width = region_width
        c_height = region_height - 20
        sub_scroll_height = c_height - 125
        sub_scroll_width = 830
        v = c_height - 35
        v -= 60

        self._players_list_button = bui.buttonwidget(
            parent=self._container,
            label="PLAYERS LIST",
            size=(120, 40),
            position=(720, v + 13),
            on_activate_call=bs.WeakCall(self._show_random_join_settings),
        )

    @override(PublicGatherTab)
    def _show_random_join_settings(self) -> None:
        PlayerListPopup(
            origin_widget=self._players_list_button)


class PlayerListPopup(bui.Window):
    def __init__(self, origin_widget: bui.Widget) -> None:
        c_width = 600
        c_height = 400
        uiscale = bui.app.ui_v1.uiscale
        super().__init__(root_widget=bui.containerwidget(
            scale=(
                1.8
                if uiscale is babase.UIScale.SMALL
                else 1.55
                if uiscale is babase.UIScale.MEDIUM
                else 1.0
            ),
            scale_origin_stack_offset=origin_widget.get_screen_space_center(),
            stack_offset=(0, -10)
            if uiscale is babase.UIScale.SMALL
            else (0, 15)
            if uiscale is babase.UIScale.MEDIUM
            else (0, 0),
            size=(c_width, c_height),
            transition='in_scale',
        ))


        bui.textwidget(
            parent=self._root_widget,
            size=(0, 0),
            h_align='center',
            v_align='center',
            text="PLAYERS LIST",
            scale=1.6,
            color=(0.6, 1.0, 0.6),
            maxwidth=c_width * 0.8,
            position=(c_width * 0.5, 330),
        )

        self._scrollwidget = bui.scrollwidget(parent=self._root_widget,
                                              size=(c_width-50, c_height-160),
                                              position=(30,60))
        self._columnwidget = bui.columnwidget(parent=self._scrollwidget,
                                              border=1,
                                              margin=0)

        self._cancel_button = btn = bui.buttonwidget(
                parent=self._root_widget,
                autoselect=True,
                position=(40, 320),
                size=(130, 60),
                scale=0.8,
                text_scale=1.2,
                label=bui.Lstr(resource='backText'),
                button_type='back',
                on_activate_call=self._transition_out,
           )

   
        threading.Thread(target=get_data_from_firebase).start()
        if data:
          for user in data["online"]:
             if str(user) != str(bui.app.plus.get_v1_account_display_string()) and data["online"][user]["ip"] != "None":
               bui.textwidget(
                           parent=self._columnwidget,
                           size=(610, 30),
                           selectable=True,
                           always_highlight=True,
                           color=(1,1,1),
                           text=str(user),
                           click_activate=True,
                           on_select_call=lambda u=user: self._get_player_game(u),
                           h_align='left',
                           v_align='center',
                           scale=1,
                           maxwidth=500)
        

        self.selected_count = 0
    def _get_player_game(self, user):
        self.selected_count += 1
        if self.selected_count >= 2:
          PlayerInfoPopup(self._root_widget, user)

    def _transition_out(self) -> None:
        bui.containerwidget(edit=self._root_widget, transition='out_scale')


class PlayerInfoPopup(bui.Window):
    def __init__(self, origin_widget: bui.Widget, user) -> None:
        c_width = 600
        c_height = 400
        uiscale = bui.app.ui_v1.uiscale
        super().__init__(root_widget=bui.containerwidget(
            scale=(
                1.8
                if uiscale is babase.UIScale.SMALL
                else 1.55
                if uiscale is babase.UIScale.MEDIUM
                else 1.0
            ),
            scale_origin_stack_offset=origin_widget.get_screen_space_center(),
            stack_offset=(0, -10)
            if uiscale is babase.UIScale.SMALL
            else (0, 15)
            if uiscale is babase.UIScale.MEDIUM
            else (0, 0),
            size=(c_width, c_height),
            transition='in_scale',
        ))


        # Cancel button.
        self.cancel_button = btn = bui.buttonwidget(
            parent=self._root_widget,
            label="BACK",
            size=(180, 60),
            color=(1.0, 0.2, 0.2),
            position=(40, 30),
            on_activate_call=self._transition_out,
            autoselect=True,
        )
        bui.containerwidget(edit=self._root_widget, cancel_button=btn)

        # Join button.
        self.savebtn = btn = bui.buttonwidget(
            parent=self._root_widget,
            label="JOIN",
            size=(180, 60),
            position=(c_width - 200, 30),
            on_activate_call=self._save,
            autoselect=True,
        )
        bui.containerwidget(edit=self._root_widget, start_button=btn)

        self.online_name = None
        self.online_ip = None
        self.online_port = None
        self.online_lastseen = None
        self.title = user+" OFFLINE"

        threading.Thread(target=get_data_from_firebase).start()
        if user in data["online"]:
          if data["online"][user]["ip"] != "None":
            player = data["online"][user]
            self.online_name = player["name"]
            self.online_ip = player["ip"]
            self.online_port = player["port"]
            self.online_lastseen = player["lastseen"]
            self.title = str(user)+" ONLINE"

        if str(self.online_lastseen) != "None":
          from datetime import datetime
          formatted_date = datetime.utcfromtimestamp(int(float(self.online_lastseen))).strftime('%m/%d/%y %I:%M%p UTC')
        else:
          formatted_date = "None"

        bui.textwidget(
            parent=self._root_widget,
            size=(0, 0),
            h_align='center',
            v_align='center',
            text=self.title,
            scale=1.5,
            color=(0.6, 1.0, 0.6),
            maxwidth=c_width * 0.8,
            position=(c_width * 0.5, c_height - 60),
        )

        v = c_height - 120
        bui.textwidget(
            parent=self._root_widget,
            size=(0, 0),
            h_align='right',
            v_align='center',
            text='NAME : ',
            maxwidth=c_width * 0.3,
            position=(c_width * 0.4, v),
        )
        self._maximum_ping_edit = bui.textwidget(
            parent=self._root_widget,
            size=(c_width * 0.3, 40),
            h_align='left',
            v_align='center',
            text=str(self.online_name),
            maxwidth=c_width * 0.3,
            position=(c_width * 0.6, v - 20),
        )
        v -= 40
        bui.textwidget(
            parent=self._root_widget,
            size=(0, 0),
            h_align='right',
            v_align='center',
            text='IP : ',
            maxwidth=c_width * 0.3,
            position=(c_width * 0.4, v),
        )
        self._minimum_players_edit = bui.textwidget(
            parent=self._root_widget,
            size=(c_width * 0.3, 40),
            h_align='left',
            v_align='center',
            text=str(self.online_ip),
            maxwidth=c_width * 0.3,
            position=(c_width * 0.6, v - 20),
        )
        v -= 40
        bui.textwidget(
            parent=self._root_widget,
            size=(0, 0),
            h_align='right',
            v_align='center',
            text='PORT : ',
            maxwidth=c_width * 0.3,
            position=(c_width * 0.4, v),
        )
        self._part_of_name_edit = bui.textwidget(
            parent=self._root_widget,
            size=(c_width * 0.3, 40),
            h_align='left',
            v_align='center',
            text=str(self.online_port),
            maxwidth=c_width * 0.3,
            position=(c_width * 0.6, v - 20),
        )
        v -= 40
        bui.textwidget(
            parent=self._root_widget,
            size=(0, 0),
            h_align='right',
            v_align='center',
            text='LAST SEEN : ',
            maxwidth=c_width * 0.3,
            position=(c_width * 0.4, v),
        )
        self._part_of_name_edit = bui.textwidget(
            parent=self._root_widget,
            size=(c_width * 0.3, 40),
            h_align='left',
            v_align='center',
            text=str(formatted_date),
            maxwidth=c_width * 0.3,
            position=(c_width * 0.6, v - 20),
        )

    def _save(self) -> None:
        if self.online_ip and self.online_port:
          bs.connect_to_party(self.online_ip, int(self.online_port))

    def _transition_out(self) -> None:
            bui.containerwidget(edit=self._root_widget, transition='out_scale')




def save_host_info(host):
    global data
    threading.Thread(target=get_data_from_firebase).start()
    data = data if data else {"all_players": {}, "online": {}}
    if host:
      data["all_players"][str(bui.app.plus.get_v1_account_display_string())] = {"name": str(host.name), "ip": str(host.address), "port": str(host.port)}
      data["online"][str(bui.app.plus.get_v1_account_display_string())] = {"name": str(host.name), "ip": str(host.address), "port": str(host.port), "lastseen": str(time.time())}
      post_data_to_firebase(data)
    else:
      data["all_players"][str(bui.app.plus.get_v1_account_display_string())] = {"name": "None", "ip": "None", "port": "None"}
      data["online"][str(bui.app.plus.get_v1_account_display_string())] = {"name": "None", "ip": "None", "port": "None", "lastseen": str(time.time())}
      post_data_to_firebase(data)

def start_save():
    host = bs.get_connection_to_host_info_2()
    threading.Thread(target=lambda: save_host_info(host)).start()
