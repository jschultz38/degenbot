def translateMonth(month_text):
	month_ret = None
	match month_text:
		case 'January' | 'Jan':
			month_ret = 1
		case 'February' | 'Feb':
			month_ret = 2
		case 'March' | 'Mar':
			month_ret = 3
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
		case 'September' | 'Sep':
			month_ret = 9
		case 'October' | 'Oct':
			month_ret = 10
		case 'November' | 'Nov':
			month_ret = 11
		case 'December' | 'Dec':
			month_ret = 12
		case _:
			print("ERROR: Could not decode: " + month_text)
			month_ret = 1

	return month_ret