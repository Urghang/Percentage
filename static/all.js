 $(document).on('click', '[id="alert"]', function(e) {

	 		var current_row = $(this).closest('tr');
	 		var part_id = current_row.find('td:eq(0)').html()
	 		var postavshik = current_row.find('td:eq(1)').html()
                        var qty =$(this).closest('td').find('input[type=number]').val();
	 		var tname = $(this).attr('tname');
	 		$.ajax({
                        	url: "/new_order/",
                        	type: "POST",
                        	data: {
					qty: qty,
					partId: part_id,
					postavshik_id: postavshik,
					stock_id: 1
					
				
                        	}



                	});

                });

