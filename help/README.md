## Create a new translation

For example german="de"

    mkdir de
    cd de
    itstool -o ./de.pot ../C/*.page
    mv de.pot de.po

and then add "de" to LINGUAS

## merge / update

    msgmerge de.po de.pot > new.po
