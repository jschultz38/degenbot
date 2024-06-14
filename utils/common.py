def translateMonth(month_text):
	month_ret = None
	match month_text:
		case 'April' | 'Apr':
			month_ret = 4
		case 'May':
			month_ret = 5
		case 'June' | 'Jun':
			month_ret = 6
		case 'July' | 'Jul':
			month_ret = 7
		case 'August' | 'Aug':
			month_ret = 8
		case 'Sep':
			month_ret = 9
		case _:
			print("ERROR: Could not decode: " + month_text)
			month_ret = 1

	return month_ret