import utils.interception as interception

kdevice = interception.listen_to_keyboard()
mdevice = interception.listen_to_mouse()


print(kdevice)
print(mdevice)
interception.inputs.keyboard = 0
interception.inputs.mouse = 10
interception.move_to(480, 540)
interception.click(120, 160, button="left", delay=1)
with interception.hold_key("shift"):
    interception.press("x")

