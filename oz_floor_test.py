import obspython as obs
import time
import threading
import cv2
import numpy as np  
import mss
import mss.tools

source_name = "test"

# ------------------------------------------------------------

overlay_enabled = False
counter = 1
thread = None

yellowDot = cv2.imread("C:\work\maplestory_oz_floor48\YellowDot.png")

def start_overlay(props, prop):
    global overlay_enabled
    global thread

    if not (overlay_enabled):
        overlay_enabled = True
        thread = threading.Thread(target=update_text, daemon=True)
        thread.start()

def stop_overlay(props, prop):
    global overlay_enabled
    global thread

    overlay_enabled = False
    
    thread.join()

def update_text():
    global overlay_enabled
    global source_name
    global counter
    
    while(overlay_enabled):
        source = obs.obs_get_source_by_name(source_name)

        index = get_x_y_coordinates()

        if source is not None:
            settings = obs.obs_data_create()
            # obs.obs_data_set_string(settings, "text", str(counter))
            obs.obs_data_set_string(settings, "text", str(index))
            obs.obs_source_update(source, settings)
            obs.obs_data_release(settings)
            obs.obs_source_release(source)
            counter += 2
        time.sleep(0.05)


def get_x_y_coordinates():

    global yellowDot

    with mss.mss() as sct:
        # baseImage = "C:\work\maplestory_oz_floor48\TestInput.png"
        baseImageName = sct.shot(mon=2)

        searchImage = "C:\work\maplestory_oz_floor48\Search.png"

        ## Get Mini map coords
        # image = cv2.imread(baseImage)
        image = cv2.imread(baseImageName)
        # searchImage = cv2.imread(searchImage)
        # result = cv2.matchTemplate(image,searchImage,cv2.TM_CCOEFF_NORMED)
        # index = np.unravel_index(result.argmax(),result.shape)

        # Capture mini map
        # croppedMiniMapImage = image[index[0]:index[0]+searchImage.shape[0], index[1]:index[1]+searchImage.shape[1]]
        # cv2.imwrite("C:/work/maplestory_oz_floor48/foundMap.png", croppedMiniMapImage)

        # Find yellow dot
        result = cv2.matchTemplate(image,yellowDot,cv2.TM_CCOEFF_NORMED)
        index = np.unravel_index(result.argmax(),result.shape)

        # Capture yellow dot area
        # yellowDotAnswer = image[index[0]-30:index[0]+30, index[1]-30:index[1]+30]
        # cv2.imwrite("C:/work/maplestory_oz_floor48/answer.png", yellowDotAnswer)


        return index


# -----------------SCRIPT PROPERTIES---------------------

def script_properties():
    """
    Called to define user properties associated with the script. These
    properties are used to define how to show settings properties to a user.
    """
    props = obs.obs_properties_create()
    p = obs.obs_properties_add_list(props, "source", "Text Source",
                                    obs.OBS_COMBO_TYPE_EDITABLE,
                                    obs.OBS_COMBO_FORMAT_STRING)
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_id(source)
            if source_id == "text_gdiplus" or source_id == "text_ft2_source":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p, name, name)

        obs.source_list_release(sources)

    obs.obs_properties_add_button(props, "button", "Start Overlay", start_overlay)
    obs.obs_properties_add_button(props, "button2", "Stop Overlay", stop_overlay)

    return props


def script_update(settings):
    """
    Called when the script’s settings (if any) have been changed by the user.
    """
    global source_name

    source_name = obs.obs_data_get_string(settings, "source")