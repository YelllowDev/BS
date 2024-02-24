import json, threading, time, urllib, datetime
import babase
import bauiv1 as bui
import bauiv1lib.party
import bascenev1 as bs 
from bauiv1lib.tabs import TabRow

data = None
# SAVE DATABASE
def post_data_to_firebase(data):
    url = 'https://yelllowdev-default-rtdb.firebaseio.com/data.json'
    data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='PUT')
    with urllib.request.urlopen(req) as f:
        data = json.loads(f.read().decode('utf-8'))

# GET DATABASE
def get_data_from_firebase():
    global data
    url = 'https://yelllowdev-default-rtdb.firebaseio.com/data.json'
    with urllib.request.urlopen(url) as f:
        response = f.read().decode('utf-8')
        data = json.loads(response)

### SOME FUNCTIONS THAT HELP ###
# FORMAT TIME
def format_time_difference(timestamp):
    time_difference = datetime.datetime.now() - datetime.datetime.fromtimestamp(timestamp)
    days = time_difference.days
    hours = time_difference.seconds // 3600
    minutes = (time_difference.seconds % 3600) // 60
    seconds = time_difference.seconds % 60
    
    if days > 0:
        return f"{days} days ago"
    elif hours > 0:
        return f"{hours} hours ago"
    elif minutes > 0:
        return f"{minutes} minutes ago"
    elif seconds > 0:
        return f"{seconds} seconds ago"
    else:
        return "Just now"

class NewPW(bauiv1lib.party.PartyWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.players_list_button = bui.buttonwidget(
            parent=self._root_widget,
            size=(100, 35),
            label='PLAYERS LIST',
            button_type='square',
            autoselect=True,
            position=(self._width - 415, self._height - 50),
            on_activate_call=self._open_players_list_window
        )

    def _open_players_list_window(self):
      PlayersListPopup(self.players_list_button)
      bui.containerwidget(edit=self._root_widget, transition='out_scale')




class PlayersListPopup(bui.Window):
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
            #color=(0.2,0.4,0.8),
            transition='in_scale',
        ))
        self.open_window_len = 0
        # TITLE 
        self._title = bui.textwidget(
            parent=self._root_widget,
            size=(0, 0),
            h_align='center',
            v_align='center',
            text="PLAYERS LIST",
            scale=1.0,
            color=(0.6, 1.0, 0.6),
            maxwidth=c_width * 0.8,
            position=(c_width * 0.5, 380),
        )
        # BACK BUTTON
        self._cancel_button = btn = bui.buttonwidget(
                parent=self._root_widget,
                autoselect=True,
                position=(40, 350),
                size=(80, 60),
                scale=0.8,
                text_scale=1.2,
                label=bui.charstr(bui.SpecialChar.BACK),
                button_type='backSmall',
                on_activate_call=self._transition_out,
           )
        # SCROLL 
        self._scrollwidget = bui.scrollwidget(parent=self._root_widget, size=(c_width-50, c_height-160), position=(30,60))
        # SCROLL COLUMNS
        self._columnwidget = bui.columnwidget(parent=self._scrollwidget, border=1, margin=0)

        #TABS 
        self._tab_row = TabRow(
            self._root_widget,
            [("all_players", "ALL PLAYERS"), ("following", "FOLLOWING")],
            pos=(28,c_height-103),
            size=(c_width-48, 50),
            on_select_call=bui.WeakCall(self._change_tab),
        )
        # SET DEFAULT TAB
        self._tab = "following"
        self._tab_row.update_appearance("all_players")
        self._change_tab("all_players")

    # CHANGE TAB
    def _change_tab(self, tab_id):
      if self._tab == tab_id:
        return

      self._tab_row.update_appearance(tab_id)
      for child in self._columnwidget.get_children():
        child.delete()
      self.open_window_len = 0
      if tab_id == "all_players":
        self._tab = "all_players"
        # GET DATA & PLACING PLAYERS ON THE LIST
        threading.Thread(target=get_data_from_firebase).start()
        if data:
          found = False
          for player in data:
            if player != str(bui.app.plus.get_v1_account_display_string()):
              found = True
              self.player_select = bui.textwidget(
                           parent=self._columnwidget,
                           size=(610, 30),
                           selectable=True,
                           always_highlight=True,
                           color=(1,1,1),
                           text=player,
                           click_activate=True,
                           on_select_call=lambda player=player: self.open_player_info_window(player),
                           h_align='left',
                           v_align='center',
                           scale=1,
                           maxwidth=500)
          if not found:
            bui.textwidget(
                           parent=self._columnwidget,
                           size=(610, 30),
                           always_highlight=True,
                           color=(1,1,1),
                           text="THERE IS NO ONE",
                           click_activate=True,
                           h_align='left',
                           v_align='center',
                           scale=1)
        
      elif tab_id == "following":
        self._tab = "following"
        self.open_window_len -= 1
        # GET DATA & PLACING PLAYERS ON THE LIST
        threading.Thread(target=get_data_from_firebase).start()
        if data:
          found = False
          for player in data[str(bui.app.plus.get_v1_account_display_string())]["following"]:
            if player != str(bui.app.plus.get_v1_account_display_string()):
              found = True
              self.player_select = bui.textwidget(
                           parent=self._columnwidget,
                           size=(610, 30),
                           selectable=True,
                           always_highlight=True,
                           color=(1,1,1),
                           text=player,
                           click_activate=True,
                           on_select_call=lambda player=player: self.open_player_info_window(player),
                           h_align='left',
                           v_align='center',
                           scale=1,
                           maxwidth=500)
          if not found:
            bui.textwidget(
                           parent=self._columnwidget,
                           size=(610, 30),
                           always_highlight=True,
                           color=(1,1,1),
                           text="YOU HAVEN'T FOLLOWED ANYONE",
                           click_activate=True,
                           h_align='left',
                           v_align='center',
                           scale=1)
      else:
        return
    
    # OPEN PLAYER INFO WINDOW
    def open_player_info_window(self, user) -> None:
      self.open_window_len += 1
      if self.open_window_len >= 2:
        PlayerInfoPopup(self.player_select, user)

    # CLOSE WINDOW
    def _transition_out(self) -> None:
        bui.containerwidget(edit=self._root_widget, transition='out_scale')


class PlayerInfoPopup(bui.Window):
    def __init__(self, origin_widget: bui.Widget, user) -> None:
        c_width = 600
        c_height = 400
        self.user_ = user
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

        # TITLE 
        self._title = bui.textwidget(
            parent=self._root_widget,
            size=(0, 0),
            h_align='center',
            v_align='center',
            text=user+" INFO",
            scale=1.0,
            color=(0.6, 1.0, 0.6),
            maxwidth=c_width * 0.8,
            position=(c_width * 0.5, 380),
        )
        # BACK BUTTON
        self._cancel_button = btn = bui.buttonwidget(
                parent=self._root_widget,
                autoselect=True,
                position=(40, 350),
                size=(80, 60),
                scale=0.8,
                text_scale=1.2,
                label=bui.charstr(bui.SpecialChar.BACK),
                button_type='backSmall',
                on_activate_call=self._transition_out,
           )


        threading.Thread(target=get_data_from_firebase).start()
        if data:
          self.user_info = data[user]

        self.lastseen = datetime.datetime.utcfromtimestamp(int(self.user_info["lastseen"])).strftime('%m/%d/%y %I:%M%p UTC')
        self.msg_time_ago = ""
        if int(time.time()) - int(self.user_info["lastseen"]) <= 5:
            self.lastseen = "Now"
        else:
            self.msg_time_ago = format_time_difference(int(self.user_info["lastseen"]))

        if self.user_info["activity"] != "None":
          self.address = self.user_info["activity"]["IP"]
          self.port = self.user_info["activity"]["PORT"]
          self.name = self.user_info["activity"]["NAME"]
          self.in_game = "Yes"
        else:
          self.address = "None"
          self.port = "None"
          self.name = "None"
          self.in_game = "No"

        v = c_height - 100
        if self.in_game == "No":
          v = c_height - 150
        bui.textwidget(
            parent=self._root_widget,
            size=(0, 0),
            h_align='right',
            v_align='center',
            text='IN GAME : ',
            maxwidth=c_width * 0.3,
            position=(c_width * 0.4, v),
        )
        self._maximum_ping_edit = bui.textwidget(
            parent=self._root_widget,
            size=(c_width * 0.3, 40),
            h_align='left',
            v_align='center',
            text=str(self.in_game),
            maxwidth=c_width * 0.3,
            position=(c_width * 0.6, v - 20),
        )
        if self.in_game == "Yes":
          v -= 50
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
            text=str(self.name),
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
            text=str(self.address),
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
            text=str(self.port),
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
            text=f"\n{self.lastseen}\n{self.msg_time_ago}",
            maxwidth=c_width * 0.3,
            position=(c_width * 0.6, v - 20),
        )

        if self.in_game == "Yes":
          # FOLLOW BUTTON
          self.follow_button = btn = bui.buttonwidget(
            parent=self._root_widget,
            label=" FOLLOW ",
            size=(180, 60),
            color=(1.0, 0.2, 0.2),
            position=(40, 30),
            on_activate_call=self._follow,
            autoselect=True,
        )
          bui.containerwidget(edit=self._root_widget, cancel_button=btn)

          # JOIN BUTTON
          self.join_button = btn = bui.buttonwidget(
            parent=self._root_widget,
            label=" JOIN ",
            size=(180, 60),
            position=(c_width - 200, 30),
            on_activate_call=self._join,
            autoselect=True,
        )
          bui.containerwidget(edit=self._root_widget, start_button=btn)
        else:
          # FOLLOW BUTTON
          self.follow_button = btn = bui.buttonwidget(
            parent=self._root_widget,
            label=" FOLLOW ",
            size=(180, 60),
            color=(1.0, 0.2, 0.2),
            position=(c_width * 0.5-90, 30),
            on_activate_call=self._follow,
            autoselect=True,
        )
          bui.containerwidget(edit=self._root_widget, cancel_button=btn)

    def _follow(self) -> None:
      my_name = str(bui.app.plus.get_v1_account_display_string())
      if self.user_ not in data[my_name]["following"]:
        data[my_name]["following"].append(self.user_)
        threading.Thread(target=lambda: post_data_to_firebase(data)).start()
        bs.screenmessage(f"You have followed {self.user_}", color=(0,1,0))
      else:
        bs.screenmessage(f"You have followed this player before", color=(1,0,0))

    def _join(self) -> None:
        if self.address != "None" and self.port != "None":
          bs.connect_to_party(self.address, int(self.port))
        else:
          bs.screenmessage("This player is not in a game", color=(1,0,0))


    # CLOSE WINDOW
    def _transition_out(self) -> None:
        bui.containerwidget(edit=self._root_widget, transition='out_scale')




# SAVE HOST INFO
def save_host_info(host):
    global data
    threading.Thread(target=get_data_from_firebase).start()
    data = data
    user = str(bui.app.plus.get_v1_account_display_string())
    if user not in data:
      data[user] = {"activity": "None", "lastseen": "None", "following": ["YelllowDev"]}
    data[user]["lastseen"] = int(time.time())
    if host:
      host_info = {"IP": str(host.address), "PORT": str(host.port), "NAME": str(host.name)}
      data[user]["activity"] = host_info
    else:
      data[user]["activity"] = "None"
    post_data_to_firebase(data)

# RUN "SAVE HOST INFO" USING THREADING
def start_save():
    host = bs.get_connection_to_host_info_2()
    threading.Thread(target=lambda: save_host_info(host)).start()

# MAKE PLAYER OFFLINE
def player_is_offline():
    global data
    threading.Thread(target=get_data_from_firebase).start()
    data = data
    user = str(bui.app.plus.get_v1_account_display_string())
    if user not in data:
      data[user] = {"activity": "None", "lastseen": "None", "following": ["YelllowDev"]}
    data[user]["lastseen"] = int(time.time())
    data[user]["activity"] = "None"
    post_data_to_firebase(data)
