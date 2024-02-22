import json, threading, urllib, time, datetime
import babase
import bauiv1 as bui
import bauiv1lib.party
import bascenev1 as bs 

# SEND DISCORD MESSAGE
messages = None
url = "https://yell00w-default-rtdb.firebaseio.com/data.json"
def send_discord_message(data):
    data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='PUT')
    with urllib.request.urlopen(req) as f:
        messages = json.loads(f.read().decode('utf-8'))
        

# GET DISCORD MESSAGES
def get_discord_messages():
    global messages
    global seen_messages
    with urllib.request.urlopen(url) as f:
        response = f.read().decode('utf-8')
        messages = json.loads(response)
        if messages is None:
          messages = []

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


# SPLIT MESSAGE
def split_msg(message):
  chunks = []
  chunk = ""
  for word in message.split():
      if len(chunk) + len(word) + 1 <= 50:
          chunk += word + " "
      else:
          chunks.append(chunk.strip())
          chunk = word + " "
  if chunk:
      chunks.append(chunk.strip())

  return chunks



class NewPW(bauiv1lib.party.PartyWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.window_ = None
        self.online_chat_button = bui.buttonwidget(
            parent=self._root_widget,
            size=(100, 35),
            label='ONLINE CHAT',
            button_type='square',
            autoselect=True,
            position=(self._width - 415, self._height - 50),
            on_activate_call=self._open_online_chat_window
        )
    def _open_online_chat_window(self):
      if self.window_:
        bui.containerwidget(edit=self.window_, transition='out_scale')
      self.window_ = OnlineChatPopup(self.online_chat_button)
      bui.containerwidget(edit=self._root_widget, transition='out_scale')




class OnlineChatPopup(bui.Window):
    def __init__(self, origin_widget: bui.Widget) -> None:
        self.c_width = 600
        self.c_height = 400
        self.uiscale = bui.app.ui_v1.uiscale
        super().__init__(root_widget=bui.containerwidget(
            scale=(
                1.8
                if self.uiscale is babase.UIScale.SMALL
                else 1.55
                if self.uiscale is babase.UIScale.MEDIUM
                else 1.0
            ),
            scale_origin_stack_offset=origin_widget.get_screen_space_center(),
            stack_offset=(0, -10)
            if self.uiscale is babase.UIScale.SMALL
            else (0, 15)
            if self.uiscale is babase.UIScale.MEDIUM
            else (0, 0),
            size=(self.c_width, self.c_height),
            #color=(0.2,0.4,0.8),
            transition='in_scale',
        ))

        # TITLE 
        self._title = bui.textwidget(
            parent=self._root_widget,
            size=(0, 0),
            h_align='center',
            v_align='center',
            text="ONLINE CHAT",
            scale=1.0,
            color=(0.6, 1.0, 0.6),
            maxwidth=self.c_width * 0.8,
            position=(self.c_width * 0.5, 380),
        )
        # MADE BY 
        self._made_by = bui.textwidget(
            parent=self._root_widget,
            size=(0, 0),
            h_align='center',
            v_align='center',
            text="MADE BY YelllowDev",
            scale=0.5,
            color=(0.6, 1.0, 0.6),
            maxwidth=self.c_width * 0.8,
            position=(self.c_width * 0.5, 360),
        )
        # BACK BUTTON
        self._cancel_button = btn = bui.buttonwidget(
                parent=self._root_widget,
                #autoselect=True,
                position=(40, 350),
                size=(80, 60),
                scale=0.8,
                text_scale=1.2,
                label=bui.charstr(bui.SpecialChar.BACK),
                button_type='backSmall',
                on_activate_call=self._transition_out,
           )
        # SCROLL 
        self._scrollwidget = bui.scrollwidget(parent=self._root_widget, size=(self.c_width-50, self.c_height-160), position=(30,90))
        # SCROLL COLUMNS
        self._columnwidget = bui.columnwidget(parent=self._scrollwidget, border=1, margin=0)
        # MESSAGE BOX
        self._message_box = bui.textwidget(
            parent=self._root_widget,
            size=(self.c_width-110, 40),
            h_align='left',
            v_align='center',
            text="",
            editable=True,
            description='Enter message ...',
            position=(35, 40),
            autoselect=True,
            max_chars=130,
        )
        # SEND BUTTON
        self._send_button = btn = bui.buttonwidget(
                parent=self._root_widget,
                autoselect=True,
                position=(538, 42),
                size=(80, 45),
                scale=0.8,
                text_scale=1.2,
                label="SEND",
                button_type='square',
                on_activate_call=self._send_message,
           )
        bui.textwidget(edit=self._message_box,on_return_press_call=self._send_button.activate)
        self._update_timer = bs.AppTimer(0.5, self._refresh, repeat=True)

    # SEND MESSAGE
    def _send_message(self):
        threading.Thread(target=get_discord_messages).start()
        global messages
        if messages is None:
          messages = []
        message = bui.textwidget(query=self._message_box)
        if message.strip() != "":
          splits = split_msg(message)
          for split in splits:
            author = str(bui.app.plus.get_v1_account_display_string())
            message = str(split)
            msg_time = str(int(time.time()))

            messages.append({"msg": message, "author": author, "time": msg_time})
            threading.Thread(target=lambda: send_discord_message(messages)).start()
            bui.textwidget(edit=self._message_box, text="")
            self._refresh()

    # CHANGE TAB
    def _refresh(self):
      try:
          for child in self._columnwidget.get_children():
              child.delete()

          threading.Thread(target=get_discord_messages).start()
          global messages
          if messages is None:
            messages = []
          for msg in messages:
              self.msg_ = bui.textwidget(
                           parent=self._columnwidget,
                           size=(610, 30),
                           selectable=True,
                           #autoselect=True,
                           #always_highlight=True,
                           color=(1,1,1),
                           text=f"{msg['author']}: {msg['msg']}",
                           click_activate=True,
                           h_align='left',
                           v_align='center',
                           on_activate_call=lambda msg=msg: self._msg_info(msg),
                           scale=1,
                           maxwidth=500)
      except:
        pass

    # MSG INFO
    def _msg_info(self, msg):
        self._root_widget2 = bui.containerwidget(size=(350, 100),
                                                on_outside_click_call=self._transition_out2,
                                                transition="in_scale",
                                                scale=(2.1 if self.uiscale is babase.UIScale.SMALL else 1.5
                                                       if self.uiscale is babase.UIScale.MEDIUM else 1.0))
        msg_time = datetime.datetime.utcfromtimestamp(int(msg['time'])).strftime('%m/%d/%y %I:%M:%S %p - UTC')
        msg_time_ago = format_time_difference(int(msg['time']))
        bui.textwidget(
                           parent=self._root_widget2,
                           size=(350, 75),
                           color=(1,1,1),
                           text=msg_time+"\n"+msg_time_ago,
                           h_align='center',
                           v_align='center',)
        try:
          admin_func(self, msg)
        except:
           pass
    # CLOSE WINDOW 1
    def _transition_out(self) -> None:
        bui.containerwidget(edit=self._root_widget, transition='out_scale')
    # CLOSE WINDOW 2
    def _transition_out2(self) -> None:
        bui.containerwidget(edit=self._root_widget2, transition='out_scale')

