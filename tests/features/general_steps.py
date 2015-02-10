from lettuce import world, step


@step(u'I see text "(\w+)"')
def see_text(step, text):
    assert world.browser.is_text_present(text)

@step(u'I go to url "(.+)"')
def go_to_url(step, url):
    world.browser.visit(url)


@step(u'I click on "(\w+)')
def click_on(step, text):
    assert world.browser.is_text_present(text)
    world.browser.find_link_by_text(text).click()

