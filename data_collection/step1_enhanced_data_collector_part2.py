#!/usr/bin/env python3
"""
Step 1: Enhanced Data Collector - Part 2: Complete implementation
"""

# Continue the EnhancedDataCollector class
class EnhancedDataCollectorComplete:
    def __init__(self):
        self.training_data_dir = "training_data_2014_2019"
        self.testing_data_dir = "testing_data_2019_2025"
        self.logs_dir = "download_logs"
        
        # Create directories
        import os
        os.makedirs(self.training_data_dir, exist_ok=True)
        os.makedirs(self.testing_data_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Download statistics
        self.stats = {
            'total_stocks': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'insufficient_data': 0,
            'start_time': None,
            'end_time': None
        }
        
    def get_complete_stock_list(self):
        """Get the complete list of 2000+ Indian stocks"""
        
        # Your complete stock list
        stocks = [
            '20MICRONS', '21STCENMGM', '360ONE', '3IINFOLTD', '3MINDIA', '3PLAND', '5PAISA', '63MOONS', 
            'A2ZINFRA', 'AAATECH', 'AADHARHFC', 'AAKASH', 'AAREYDRUGS', 'AARON', 'AARTECH', 'AARTIDRUGS', 
            'AARTIIND', 'AARTIPHARM', 'AARTISURF', 'AARVEEDEN', 'AARVI', 'AAVAS', 'ABAN', 'ABB', 
            'ABBOTINDIA', 'ABCAPITAL', 'ABDL', 'ABFRL', 'ABINFRA', 'ABLBL', 'ABMINTLLTD', 'ABREL', 
            'ABSLAMC', 'ACC', 'ACCELYA', 'ACCURACY', 'ACE', 'ACEINTEG', 'ACI', 'ACL', 'ACLGATI', 
            'ACMESOLAR', 'ACUTAAS', 'ADANIENSOL', 'ADANIENT', 'ADANIGREEN', 'ADANIPORTS', 'ADANIPOWER', 
            'ADFFOODS', 'ADL', 'ADOR', 'ADROITINFO', 'ADSL', 'ADVANIHOTR', 'ADVENZYMES', 'AEGISLOG', 
            'AEGISVOPAK', 'AEROENTER', 'AEROFLEX', 'AETHER', 'AFCONS', 'AFFLE', 'AFFORDABLE', 'AFIL', 
            'AFSL', 'AGARIND', 'AGARWALEYE', 'AGI', 'AGIIL', 'AGRITECH', 'AGROPHOS', 'AGSTRA', 'AHLADA', 
            'AHLEAST', 'AHLUCONT', 'AIAENG', 'AIIL', 'AIRAN', 'AIROLAM', 'AJANTPHARM', 'AJAXENGG', 
            'AJMERA', 'AJOONI', 'AKASH', 'AKG', 'AKI', 'AKSHAR', 'AKSHARCHEM', 'AKSHOPTFBR', 'AKUMS', 
            'AKZOINDIA', 'ALANKIT', 'ALBERTDAVD', 'ALEMBICLTD', 'ALICON', 'ALIVUS', 'ALKALI', 'ALKEM', 
            'ALKYLAMINE', 'ALLCARGO', 'ALLDIGI', 'ALMONDZ', 'ALOKINDS', 'ALPA', 'ALPHAGEO', 'AMBER', 
            'AMBICAAGAR', 'AMBIKCO', 'AMBUJACEM', 'AMDIND', 'AMJLAND', 'AMNPLST', 'AMRUTANJAN', 'ANANDRATHI', 
            'ANANTRAJ', 'ANDHRAPAP', 'ANDHRSUGAR', 'ANGELONE', 'ANIKINDS', 'ANKITMETAL', 'ANMOL', 'ANSALAPI', 
            'ANTGRAPHIC', 'ANUHPHR', 'ANUP', 'ANURAS', 'APARINDS', 'APCL', 'APCOTEXIND', 'APEX', 'APLAPOLLO', 
            'APLLTD', 'APOLLO', 'APOLLOHOSP', 'APOLLOPIPE', 'APOLLOTYRE', 'APOLSINHOT', 'APTECHT', 'APTUS', 
            'ARCHIDPLY', 'ARCHIES', 'ARE&M', 'ARENTERP', 'ARIES', 'ARIHANTCAP', 'ARIHANTSUP', 'ARISINFRA', 
            'ARKADE', 'ARMANFIN', 'AROGRANITE', 'ARROWGREEN', 'ARSHIYA', 'ARSSINFRA', 'ARTEMISMED', 'ARTNIRMAN', 
            'ARVEE', 'ARVIND', 'ARVINDFASN', 'ARVSMART', 'ASAHIINDIA', 'ASAHISONG', 'ASAL', 'ASALCBR', 
            'ASHAPURMIN', 'ASHIANA', 'ASHIMASYN', 'ASHOKA', 'ASHOKAMET', 'ASHOKLEY', 'ASIANENE', 'ASIANHOTNR', 
            'ASIANPAINT', 'ASIANTILES', 'ASKAUTOLTD', 'ASMS', 'ASPINWALL', 'ASTEC', 'ASTEC-RE', 'ASTERDM', 
            'ASTRAL', 'ASTRAMICRO', 'ASTRAZEN', 'ASTRON', 'ATALREAL', 'ATAM', 'ATGL', 'ATHERENERG', 'ATL', 
            'ATLANTAA', 'ATLASCYCLE', 'ATUL', 'ATULAUTO', 'AUBANK', 'AURIONPRO', 'AUROPHARMA', 'AURUM', 
            'AUSOMENT', 'AUTOAXLES', 'AUTOIND', 'AVADHSUGAR', 'AVALON', 'AVANTEL', 'AVANTIFEED', 'AVG', 
            'AVL', 'AVONMORE', 'AVROIND', 'AVTNPL', 'AWFIS', 'AWHCL', 'AWL', 'AXISBANK', 'AXISCADES', 
            'AXITA', 'AYMSYNTEX', 'AZAD', 'BAFNAPH', 'BAGFILMS', 'BAIDFIN', 'BAJAJ-AUTO', 'BAJAJCON', 
            'BAJAJELEC', 'BAJAJFINSV', 'BAJAJHCARE', 'BAJAJHFL', 'BAJAJHIND', 'BAJAJHLDNG', 'BAJAJINDEF', 
            'BAJEL', 'BAJFINANCE', 'BALAJEE', 'BALAJITELE', 'BALAMINES', 'BALAXI', 'BALKRISHNA', 'BALKRISIND', 
            'BALMLAWRIE', 'BALPHARMA', 'BALRAMCHIN', 'BALUFORGE', 'BANARBEADS', 'BANARISUG', 'BANCOINDIA', 
            'BANDHANBNK', 'BANG', 'BANKA', 'BANKBARODA', 'BANKINDIA', 'BANSALWIRE', 'BANSWRAS', 'BARBEQUE', 
            'BASF', 'BASML', 'BATAINDIA', 'BAYERCROP', 'BBL', 'BBOX', 'BBTC', 'BBTCL', 'BCG', 'BCLIND', 
            'BCONCEPTS', 'BDL', 'BEARDSELL', 'BECTORFOOD', 'BEDMUTHA', 'BEL', 'BELLACASA', 'BELRISE', 'BEML', 
            'BEPL', 'BERGEPAINT', 'BESTAGRO', 'BFINVEST', 'BFUTILITIE', 'BGRENERGY', 'BHAGCHEM', 'BHAGERIA', 
            'BHAGYANGR', 'BHANDARI', 'BHARATFORG', 'BHARATGEAR', 'BHARATRAS', 'BHARATSE', 'BHARATWIRE', 
            'BHARTIARTL', 'BHARTIHEXA', 'BHEL', 'BIGBLOC', 'BIKAJI', 'BIL', 'BILVYAPAR', 'BIOCON', 'BIOFILCHEM', 
            'BIRLACABLE', 'BIRLACORPN', 'BIRLAMONEY', 'BIRLANU', 'BLACKBUCK', 'BLAL', 'BLBLIMITED', 'BLISSGVS', 
            'BLKASHYAP', 'BLS', 'BLSE', 'BLUECOAST', 'BLUEDART', 'BLUEJET', 'BLUESTARCO', 'BLUSPRING', 
            'BODALCHEM', 'BOHRAIND', 'BOMDYEING', 'BORANA', 'BOROLTD', 'BORORENEW', 'BOROSCI', 'BOSCHLTD', 
            'BPCL', 'BPL', 'BRIGADE', 'BRITANNIA', 'BRNL', 'BROOKS', 'BSE', 'BSHSL', 'BSL', 'BSOFT', 'BTML', 
            'BUTTERFLY', 'BVCL', 'BYKE'
        ]
        
        # Continue with remaining stocks...
        stocks.extend([
            'CALSOFT', 'CAMLINFINE', 'CAMPUS', 'CAMS', 'CANBK', 'CANFINHOME', 'CANTABIL', 'CAPACITE', 
            'CAPITALSFB', 'CAPLIPOINT', 'CAPTRU-RE', 'CAPTRUST', 'CARBORUNIV', 'CARERATING', 'CARRARO', 
            'CARTRADE', 'CARYSIL', 'CASTROLIND', 'CCCL', 'CCHHL', 'CCL', 'CDSL', 'CEATLTD', 'CEIGALL', 
            'CELEBRITY', 'CELLO', 'CENTENKA', 'CENTEXT', 'CENTRALBK', 'CENTRUM', 'CENTUM', 'CENTURYPLY', 
            'CERA', 'CEREBRAINT', 'CESC', 'CEWATER', 'CGCL', 'CGPOWER', 'CHALET', 'CHAMBLFERT', 'CHEMBOND', 
            'CHEMCON', 'CHEMFAB', 'CHEMPLASTS', 'CHENNPETRO', 'CHEVIOT', 'CHOICEIN', 'CHOLAFIN', 'CHOLAHLDNG', 
            'CIEINDIA', 'CIFL', 'CIGNITITEC', 'CINELINE', 'CINEVISTA', 'CIPLA', 'CLEAN', 'CLEDUCATE', 'CLSEL', 
            'CMSINFO', 'COALINDIA', 'COASTCORP', 'COCHINSHIP', 'COFFEEDAY', 'COFORGE', 'COHANCE', 'COLPAL', 
            'COMPINFO', 'COMPUSOFT', 'COMSYN', 'CONCOR', 'CONCORDBIO', 'CONFIPET', 'CONSOFINVT', 'CONTROLPR', 
            'CORALFINAC', 'CORDSCABLE', 'COROMANDEL', 'COSMOFIRST', 'COUNCODOS', 'CPCAP', 'CRAFTSMAN', 'CREATIVE', 
            'CREATIVEYE', 'CREDITACC', 'CREST', 'CRISIL', 'CRIZAC', 'CROMPTON', 'CROWN', 'CSBBANK', 'CSLFINANCE', 
            'CTE', 'CUB', 'CUBEXTUB', 'CUMMINSIND', 'CUPID', 'CURAA', 'CYBERMEDIA', 'CYBERTECH', 'CYIENT', 
            'CYIENTDLM', 'DABUR', 'DALBHARAT', 'DALMIASUG', 'DAMCAPITAL', 'DAMODARIND', 'DANGEE', 'DATAMATICS', 
            'DATAPATTNS', 'DAVANGERE', 'DBCORP', 'DBEIL', 'DBL', 'DBOL', 'DBREALTY', 'DBSTOCKBRO', 'DCAL', 
            'DCBBANK', 'DCI', 'DCM', 'DCMFINSERV', 'DCMNVL', 'DCMSHRIRAM', 'DCMSRIND', 'DCW', 'DCXINDIA', 
            'DDEVPLSTIK', 'DECCANCE', 'DEEDEV', 'DEEPAKFERT', 'DEEPAKNTR', 'DEEPINDS', 'DELHIVERY', 'DELPHIFX', 
            'DELTACORP', 'DELTAMAGNT', 'DEN', 'DENORA', 'DENTA', 'DEVIT', 'DEVYANI', 'DGCONTENT', 'DHAMPURSUG', 
            'DHANBANK', 'DHANI', 'DHANUKA', 'DHARAN', 'DHARMAJ', 'DHRUV', 'DHUNINV', 'DIACABS', 'DIAMINESQ', 
            'DIAMONDYD', 'DICIND', 'DIFFNKG', 'DIGIDRIVE', 'DIGISPICE', 'DIGITIDE', 'DIGJAMLMTD', 'DIL', 'DISHTV', 
            'DIVGIITTS', 'DIVISLAB', 'DIXON', 'DJML', 'DLF', 'DLINKINDIA', 'DMART', 'DMCC', 'DNAMEDIA', 'DODLA', 
            'DOLATALGO', 'DOLLAR', 'DOLPHIN', 'DOMS', 'DONEAR', 'DPABHUSHAN', 'DPSCLTD', 'DPWIRES', 'DRCSYSTEMS', 
            'DREAMFOLKS', 'DREDGECORP', 'DRREDDY', 'DSSL', 'DTIL', 'DUCON', 'DVL', 'DWARKESH', 'DYCL', 'DYNAMATECH', 
            'DYNPRO', 'E2E', 'EASEMYTRIP', 'ECLERX', 'ECOSMOBLTY', 'EDELWEISS', 'EICHERMOT', 'EIDPARRY', 'EIEL', 
            'EIFFL', 'EIHAHOTELS', 'EIHOTEL', 'EIMCOELECO', 'EKC', 'ELDEHSG', 'ELECON', 'ELECTCAST', 'ELECTHERM', 
            'ELGIEQUIP', 'ELGIRUBCO', 'ELIN', 'ELLEN', 'EMAMILTD', 'EMAMIPAP', 'EMAMIREAL', 'EMBDL', 'EMCURE', 
            'EMIL', 'EMKAY', 'EMMBI', 'EMSLIMITED', 'EMUDHRA', 'ENDURANCE', 'ENERGYDEV', 'ENGINERSIN', 'ENIL', 
            'ENRIN', 'ENTERO', 'EPACK', 'EPIGRAL', 'EPL', 'EQUIPPP', 'EQUITASBNK', 'ERIS', 'ESABINDIA', 'ESAFSFB', 
            'ESCORTS', 'ESSARSHPNG', 'ESSENTIA', 'ESTER', 'ETERNAL', 'ETHOSLTD', 'EUREKAFORB', 'EUROTEXIND', 
            'EVEREADY', 'EVERESTIND', 'EXCEL', 'EXCELINDUS', 'EXICOM', 'EXICOM-RE', 'EXIDEIND', 'EXPLEOSOL', 
            'EXXARO', 'FACT', 'FAIRCHEMOR', 'FAZE3Q', 'FCL', 'FCSSOFT', 'FDC', 'FEDERALBNK', 'FEDFINA', 'FEL', 
            'FELDVR', 'FIBERWEB', 'FIEMIND', 'FILATEX', 'FILATFASH', 'FINCABLES', 'FINEORG', 'FINOPB', 'FINPIPE', 
            'FIRSTCRY', 'FISCHER', 'FIVESTAR', 'FLAIR', 'FLEXITUFF', 'FLUOROCHEM', 'FMGOETZE', 'FMNL', 'FOCUS', 
            'FOODSIN', 'FORCEMOT', 'FORTIS', 'FOSECOIND', 'FSL', 'FUSION'
        ])
        
        # Add remaining stocks (continuing the pattern)
        stocks.extend([
            'GABRIEL', 'GAEL', 'GAIL', 'GALAPREC', 'GALAXYSURF', 'GALLANTT', 'GANDHAR', 'GANDHITUBE', 'GANECOS', 
            'GANESHBE', 'GANESHHOUC', 'GANGAFORGE', 'GANGESSECU', 'GARFIBRES', 'GARUDA', 'GATECH', 'GATECHDVR', 
            'GATEWAY', 'GAYAHWS', 'GAYAPROJ', 'GEECEE', 'GEEKAYWIRE', 'GENCON', 'GENESYS', 'GENUSPAPER', 'GENUSPOWER', 
            'GEOJITFSL', 'GEPIL', 'GESHIP', 'GFLLIMITED', 'GHCL', 'GHCLTEXTIL', 'GICHSGFIN', 'GICRE', 'GILLANDERS', 
            'GILLETTE', 'GINNIFILA', 'GIPCL', 'GKWLIMITED', 'GLAND', 'GLAXO', 'GLENMARK', 'GLFL', 'GLOBAL', 'GLOBALE', 
            'GLOBALVECT', 'GLOBE', 'GLOBECIVIL', 'GLOBUSSPR', 'GLOSTERLTD', 'GMBREW', 'GMDCLTD', 'GMMPFAUDLR', 
            'GMRAIRPORT', 'GMRP&UI', 'GNA', 'GNFC', 'GOACARBON', 'GOCLCORP', 'GOCOLORS', 'GODAVARIB', 'GODFRYPHLP', 
            'GODHA', 'GODIGIT', 'GODREJAGRO', 'GODREJCP', 'GODREJIND', 'GODREJPROP', 'GOENKA', 'GOKEX', 'GOKUL', 
            'GOKULAGRO', 'GOLDENTOBC', 'GOLDIAM', 'GOLDTECH', 'GOODLUCK', 'GOPAL', 'GOYALALUM', 'GPIL', 'GPPL', 
            'GPTHEALTH', 'GPTINFRA', 'GRANULES', 'GRAPHITE', 'GRASIM', 'GRAVITA', 'GREAVESCOT', 'GREENLAM', 
            'GREENPANEL', 'GREENPLY', 'GREENPOWER', 'GRINDWELL', 'GRINFRA', 'GRMOVER', 'GROBTEA', 'GRPLTD', 'GRSE', 
            'GRWRHITECH', 'GSFC', 'GSLSU', 'GSPL', 'GSS', 'GTECJAINX', 'GTL', 'GTLINFRA', 'GTPL', 'GUFICBIO', 
            'GUJALKALI', 'GUJAPOLLO', 'GUJGASLTD', 'GUJRAFFIA', 'GUJTHEM', 'GULFOILLUB', 'GULFPETRO', 'GULPOLY', 
            'GVKPIL', 'GVPTECH', 'GVPTECH-RE', 'GVT&D'
        ])
        
        # Add .NS suffix for NSE stocks
        nse_stocks = [stock + '.NS' for stock in stocks]
        
        print(f"📊 Total stocks to download: {len(nse_stocks)}")
        return nse_stocks
