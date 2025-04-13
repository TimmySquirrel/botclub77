import re, html, logging

logger = logging.getLogger(__name__)

_PVK = r'\[((?:id|club|event){1}\d+.*)\|(.*)\]'
_PAlias = r'\[#alias\|(.*)\|(.*)\]'
_POther = r'\[(https://.*)\|(.*)\]'
_PSimOther = r'\[.*(https://.*)\]'


def ReplaceLink4MSG(aString: str, aMode)->str: 
    # aString = aString.replace('_', '\_')
    logger.info("ReplaceLink4MSG...")
    try:
        if aMode == "Markdown": 
            aString = RepVKLink(aString, r'[\2](https://vk.com/\1)')
            aString = RepAlias(aString, r'[\1](\2)') 
            aString = RepOther(aString, r'[\2](\1)') 
        elif  aMode == "HTML":  
            aString = html.escape(aString)
            aString = RepVKLinkByHTML(aString, r'<a href="https://vk.com/\1">\2</a>')
            aString = RepAliasByHTML(aString, r"<a href='\2'>\1</a>") 
            aString = RepOtherByHTML(aString, r"<a href='\1'>\2</a>") 
    except Exception as error:
        logger.error(f"ReplaceLink4MSG[{type(error)}:{error}]")
    finally:
        return aString 

def ReplaceLink4Photo(aString: str)->str:
    logger.info("ReplaceLink4Photo...")
    try:
        aString = RepVKLink(aString, r'[\2](https://vk.com/\1)')
        aString = RepAlias(aString, r'(\2)') 
        aString = RepOther(aString, r'[\2](\1)') 
        aString = RepSim(aString, r'(\1)')
    except Exception as error:
        logger.error(f"ReplaceLink4MSG[{type(error)}:{error}]") 
    finally:
        return aString 


def RepAlias(aString:str, aOutString)->str:
    return re.sub(_PAlias, aOutString, aString)  

def RepVKLink(aString:str, aOutString)->str:
    return re.sub(_PVK, aOutString, aString)  

def RepOther(aString:str, aOutString)->str:   
    return re.sub(_POther, aOutString, aString) 

def RepSim(aString:str, aOutString)->str:   
    return re.sub(_PSimOther, aOutString, aString) 

def RepAliasByHTML(aString:str, aOutString)->str:
    return re.sub(_PAlias, aOutString, aString)  

def RepVKLinkByHTML(aString:str, aOutString)->str:
    return re.sub(_PVK, aOutString, aString) 

def RepOtherByHTML(aString:str, aOutString)->str:   
    return re.sub(_POther, aOutString, aString)  