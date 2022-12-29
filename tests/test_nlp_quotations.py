from dna.nlp import resolve_quotations

text1 = 'U.S. Rep. Liz Cheney conceded defeat Tuesday in the Republican primary in Wyoming, ' \
        'an outcome that was a priority for former President Donald Trump.'
text2 = '“No House seat, no office in this land is more important than the principles we swore to ' \
        'protect,” Ms. Cheney said in her concession speech.'
text3 = '“No House seat, no office in this land is more important than the principles we swore to ' \
        'protect,” Ms. Cheney said in her concession speech. “Our nation is barreling once again toward ' \
        'crisis, lawlessness and violence. No American should support election deniers.”'
text4 = '“This is a wonderful result for America, and a complete rebuke of the Unselect Committee of ' \
        'political Hacks and Thugs,” Mr. Trump posted on Truth Social. “Now [Cheney] can finally ' \
        'disappear into the depths of political oblivion where, I am sure, she will be much happier ' \
        'than she is right now.” Trump reacted with “pure delight” over Ms. Cheney\'s loss.'
text5 = 'That was evident in her paraphrase of a quote popularized by the Rev. Dr. Martin Luther King Jr. — ' \
        '“It has been said that the long arc of history bends toward justice and freedom. That’s true, but ' \
        'only if we make it bend” — and even more so a few minutes later, when she turned her attention to ' \
        'the Civil War.'
text6 = 'After comparing herself to Lincoln, Cheney focused on the January 6 Capitol Riots and ' \
        'claimed that “America will never be the same” if Americans do not “hold those ' \
        'responsible to account.”'
text7 = 'She also claimed that Trump is promoting an “insidious lie” about the recent FBI raid of his Mar-a-Lago ' \
        'residence, which will “provoke violence and threats of violence.”'


def test_text1():
    updated_text, quotations, quotation_dict = resolve_quotations(text1)
    assert updated_text == text1
    assert not quotations and not quotation_dict


def test_text2():
    updated_text, quotations, quotation_dict = resolve_quotations(text2)
    assert updated_text == 'Quotation0 Ms. Cheney said in her concession speech.'
    assert len(quotations) == 1
    assert len(quotation_dict) == 1
    assert quotation_dict['Quotation0'] == \
           'No House seat, no office in this land is more important than the principles we swore to protect'


def test_text3():
    updated_text, quotations, quotation_dict = resolve_quotations(text3)
    assert updated_text == 'Quotation0 Ms. Cheney said in her concession speech. Quotation1 Quotation2'
    assert quotations == [
        'No House seat, no office in this land is more important than the principles we swore to protect',
        'Our nation is barreling once again toward crisis, lawlessness and violence',
        'No American should support election deniers']
    assert len(quotation_dict) == 3
    assert quotation_dict['Quotation1'] == \
           'Our nation is barreling once again toward crisis, lawlessness and violence'
    assert quotation_dict['Quotation2'] == 'No American should support election deniers'


def test_text4():
    updated_text, quotations, quotation_dict = resolve_quotations(text4)
    assert updated_text == 'Quotation0 Mr. Trump posted on Truth Social. Quotation1 ' \
                           'Trump reacted with pure delight over Ms. Cheney\'s loss.'
    assert quotations == [
        'This is a wonderful result for America, and a complete rebuke of the Unselect Committee of '
        'political Hacks and Thugs',
        'Now [Cheney] can finally disappear into the depths of political oblivion where, I am sure, '
        'she will be much happier than she is right now',
        'pure delight']
    assert len(quotation_dict) == 2
    assert quotation_dict['Quotation0'] == \
           'This is a wonderful result for America, and a complete rebuke of the Unselect Committee of ' \
           'political Hacks and Thugs'
    assert quotation_dict['Quotation1'] == \
           'Now [Cheney] can finally disappear into the depths of political oblivion where, I am sure, ' \
           'she will be much happier than she is right now'


def test_text5():
    updated_text, quotations, quotation_dict = resolve_quotations(text5)
    assert updated_text == \
           'That was evident in her paraphrase of a quote popularized by the Rev. Dr. Martin Luther King Jr. ' \
           'Quotation0 Quotation1 and even more so a few minutes later when she turned her attention to ' \
           'the Civil War.'
    assert len(quotations) == 2
    assert len(quotation_dict) == 2


def test_text6():
    updated_text, quotations, quotation_dict = resolve_quotations(text6)
    assert updated_text == \
           'After comparing herself to Lincoln Cheney focused on the January 6 Capitol Riots and claimed that ' \
           'Quotation0 if Americans do not hold those responsible to account.'
    assert len(quotations) == 2
    assert len(quotation_dict) == 1
    assert quotation_dict['Quotation0'] == 'America will never be the same'


def test_text7():
    updated_text, quotations, quotation_dict = resolve_quotations(text7)
    assert updated_text == \
           'She also claimed that Trump is promoting an insidious lie about the recent FBI raid of his ' \
           'Mar-a-Lago residence which will provoke violence and threats of violence.'
    assert len(quotations) == 2
    assert not quotation_dict
