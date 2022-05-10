import helpfunctions as hp
coin = 'ETH'
base = 'USDC'


def CreateGrid(coin, base, lowerBound, upperBound, takeProfit):
	priceLevelList = []
	priceLevel = lowerBound
	priceLevelList.append(priceLevel) 
	while priceLevel < upperBound:
		priceLevel = priceLevel + (priceLevel * (takeProfit/100))
		priceLevel = hp.round_decimals_down(priceLevel,0)
		priceLevelList.append(priceLevel)

	return priceLevelList


print(CreateGrid(coin, base, 2500, 3500, 3))
