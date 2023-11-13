# posudjenice
A dataset of loanwords in the Croatian language including language of origin, definition, part of speech and other information.
The dataset is in the Croatian language.

# Release
Release 1.0.

# Author
The author is *[Mihael Radeljić](https://github.com/MagicniJohnson)*.

# Dataset information
An datapoint consists of a loanword in Croatian and its language of origin, its definition in both croatian and language of origin, the language of origin, type of loanword, part of speech and grammatical gender (if the word is a noun). Also, the type of loanword is also given in "type", for more information look at the link in the additional information section.
Let's take "lumbrela" for example:
    _id: This field contains a unique identifier for the datapoint. It appears to be represented as an ObjectId in MongoDB, with the value "655247c76d3973e42ea5bbe3."

    word:
        word_cro: The Croatian translation or equivalent of the word, which is "lumbrela" in this case.
        word_orig_lang: The original language of the word, which is "ombrello" in Italian.

    definition:
        definition_cro: The Croatian translation or equivalent of the definition, which is "kišobran" in this case.
        definition_orig_lang: The original language of the definition, which is "kišobran" in Croatian.

    type: Indicates the type of word. In this case, it is "usvojenica," which can be translated to "adopted" or "borrowed" in English.

    example: Provides an example sentence using the word. In this example, "Padala je kiša, a nisam imala lumbrelu sa sobom," translates to "It was raining, and I didn't have an umbrella with me."

    orig_lang: Specifies the original language of the word and example sentence, which is "talijanski" (Italian) in this case.

    type_word: Describes the type of the word. In this case, it is "imenica," which translates to "noun" in English.

    gender: Specifies the gender of the noun. In this example, it is "ž," indicating feminine gender.
# Additional information
Supplemental information on some words can be found on *[HJP](https://hjp.znanje.hr/index.php?show=main)*.
More information on the type of Croatian loadwords can be found here *[link](https://hr.wikipedia.org/wiki/Posu%C4%91enice)*.

# Licence information 
 Posuđenice u hrvatskom jeziku by Mihael Radeljić is marked with CC0 1.0. 
 To view a copy of this license, visit http://creativecommons.org/publicdomain/zero/1.0
