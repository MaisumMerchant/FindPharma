from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
import cv2
import pytesseract
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import random


class ScreenOne(Screen):
    def on_enter(self):
        Clock.schedule_once(self.switch_to_screen_two, 5)

    def switch_to_screen_two(self, dt):
        self.manager.current = "screen_two"


class ScreenTwo(Screen):
    pass


class ScreenThree(Screen):
    pass


class ScreenFour(Screen):
    def on_enter(self):
        Clock.schedule_once(App.get_running_app().stop(), 5)


class CustomScreen(Screen):
    result_text = ""

    def __init__(self, **kwargs):
        super(CustomScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical")
        self.camera = Camera(
            resolution=(600, 1300),
            play=True,
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=False,
        )
        self.layout.add_widget(self.camera)
        self.capture_button = Button(text="Capture", size_hint=(1, 0.1))
        self.capture_button.bind(on_press=self.capture)
        self.layout.add_widget(self.capture_button)
        self.add_widget(self.layout)

    def capture(self, *args):
        self.camera.export_to_png("image.png")
        image = cv2.imread("image.png")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite("gray.png", gray)
        text = pytesseract.image_to_string(gray)
        href_value = self.get_href_value(text, index=2)
        self.display_href_value(href_value)
        screen_three = self.manager.get_screen("screen_three")
        for child in screen_three.children:
            if isinstance(child, Button):
                # Update the text of the first button
                child.text = self.result_text
                break
        self.manager.current = "screen_three"

    def get_href_value(self, search_text, index):
        driver = webdriver.Chrome()
        driver.get("https://www.pakmedinet.com/drugsearch.php")
        input_field = driver.find_element(By.CLASS_NAME, "search-text")
        input_field.send_keys(search_text.split()[0])
        input_field.send_keys(Keys.ENTER)
        links = driver.find_elements(By.TAG_NAME, "a")
        count = 0
        for link in links:
            if (
                link.get_attribute("href")
                and not link.get_attribute("class")
                and not link.get_attribute("id")
            ):
                count += 1
                if count == index:
                    link_html = link.get_attribute("outerHTML")
                    driver.quit()
                    return self.extract_href_value(link_html)
        driver.quit()
        return None

    def extract_href_value(self, link_html):
        soup = BeautifulSoup(link_html, "html.parser")
        href_value = soup.a["href"]
        return href_value

    def display_href_value(self, href_value):
        driver = webdriver.Chrome()
        driver.get("https://www.pakmedinet.com/" + href_value)
        a_tags = driver.find_elements(By.TAG_NAME, "a")
        filtered_a_tags = []
        for tag in a_tags:
            href = tag.get_attribute("href")
            if href and not tag.get_attribute("class") and not tag.get_attribute("id"):
                filtered_a_tags.append(tag)
        if filtered_a_tags:
            num_links_to_display = 5
            filtered_a_tags = filtered_a_tags[6:-5]
            random_a_tags = random.sample(
                filtered_a_tags, min(num_links_to_display, len(filtered_a_tags))
            )
            for tag in random_a_tags:
                self.result_text += tag.text + "\n"
        else:
            print("No Medicine Found.")
        driver.quit()


class PharmaApp(App):

    def build(self):
        Window.size = (300, 650)
        sm = ScreenManager()

        screen_one = ScreenOne(name="screen_one")
        screen_one_image = Image(
            source="screen1.jpg", allow_stretch=True, keep_ratio=False
        )
        screen_one_image.pos_hint = {"x": 0, "y": 0}
        screen_one_image.size_hint = (1, 1)
        screen_one.add_widget(screen_one_image)

        screen_two = ScreenTwo(name="screen_two")
        screen_two_image = Image(
            source="screen2.jpg", allow_stretch=True, keep_ratio=False
        )
        screen_two_image.pos_hint = {"x": 0, "y": 0}
        screen_two_image.size_hint = (1, 1)
        screen_two.add_widget(screen_two_image)

        button = Button(background_color=(0, 0, 0, 0))
        button.pos_hint = {"center_x": 0.5, "y": 0.1675}
        button.size_hint = (0.525, 0.16)
        button.bind(on_press=self.switch_to_custom_screen)
        screen_two.add_widget(button)

        custom_screen = CustomScreen(name="custom_screen")

        screen_three = ScreenThree(name="screen_three")
        screen_three_image = Image(
            source="screen3.jpg", allow_stretch=True, keep_ratio=False
        )
        screen_three_image.pos_hint = {"x": 0, "y": 0}
        screen_three_image.size_hint = (1, 1)
        screen_three.add_widget(screen_three_image)

        button2 = Button(background_color=(0, 0, 0, 0), text=" ")
        button2.pos_hint = {"center_x": 0.5, "y": 0.025}
        button2.size_hint = (0.525, 0.06)
        button2.bind(on_press=self.switch_to_screen_four)
        screen_three.add_widget(button2)

        label = Button(background_color=(0, 0, 0, 0), text=" ", color=(0, 0, 0, 1))
        label.pos_hint = {"x": 0.075, "y": 0.125}
        label.size_hint = (0.85, 0.325)
        screen_three.add_widget(label)

        screen_four = ScreenFour(name="screen_four")
        screen_four_image = Image(
            source="screen4.jpg", allow_stretch=True, keep_ratio=False
        )
        screen_four_image.pos_hint = {"x": 0, "y": 0}
        screen_four_image.size_hint = (1, 1)
        screen_four.add_widget(screen_four_image)

        sm.add_widget(screen_one)
        sm.add_widget(screen_two)
        sm.add_widget(custom_screen)
        sm.add_widget(screen_three)
        sm.add_widget(screen_four)

        return sm

    def switch_to_custom_screen(self, dt):
        self.root.current = "custom_screen"

    def switch_to_screen_four(self, dt):
        self.root.current = "screen_four"


if __name__ == "__main__":
    PharmaApp().run()
