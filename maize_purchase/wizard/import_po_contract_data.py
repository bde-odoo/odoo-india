# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import datetime
from openerp.osv import fields, osv
import csv
import logging
from openerp import netsvc
_logger = logging.getLogger("Indent Indent")

class import_po_contract_data(osv.osv_memory):
    _name = "import.po.contract.data"
    
    def _read_csv_data(self, cr, uid, path, context=None):
        """
            Reads CSV from given path and Return list of dict with Mapping
        """
        data = csv.reader(open(path))
        # Read the column names from the first line of the file
        fields = data.next()
        data_lines = []
        for row in data:
            items = dict(zip(fields, row))
            data_lines.append(items)
        return fields,data_lines
    
    def do_import_po_contract_data(self, cr, uid,ids, context=None):
        
        file_path = "/home/ashvin/Desktop/script/CONTRACT.csv"
        fields = data_lines = False
        try:
            fields, data_lines = self._read_csv_data(cr, uid, file_path, context)
        except:
            _logger.warning("Can not read source file(csv) '%s', Invalid file path or File not reachable on file system."%(file_path))
            return True            

        _logger.info("Starting Import CONTRACT HEADER Process from file '%s'."%(file_path))
        po_pool =self.pool.get('purchase.order')
        indent = []
        rejected =[]
        exist = []
        for data in data_lines:
            try:
                name = data["JOBNO"]
                if not name in exist:
                    if data["JOBNO"]:
                        exist.append(name)
                    if data["JOBNO"] and data["JOBSERIES"]:
                        old_id = data["JOBSERIES"] + '/' +data["JOBNO"]
    
                    if data["JOBSERIES"]:
                        po_series = self.pool.get('product.order.series').search(cr,uid,[('code','=','CO')])[0]
                        
                    if data["JOBDATE"]:
                        if data["JOBDATE"] == 'NULL' or data["JOBDATE"] == '' or data["JOBDATE"] == '00:00.0' or data["JOBDATE"] == '  ':
                            value = ''
                        else:
                            value=datetime.datetime.strptime(data["JOBDATE"], '%d/%m/%Y').strftime("%Y-%m-%d")
                        podate = value
    
                    if data["FROMDATE"]:
                        if data["FROMDATE"] == 'NULL' or data["FROMDATE"] == '' or data["FROMDATE"] == '00:00.0' or data["FROMDATE"] == '  ':
                            value = ''
                        else:
                            value=datetime.datetime.strptime(data["FROMDATE"], '%d/%m/%Y').strftime("%Y-%m-%d")
                        fdate = value
                        
                    if data["TODATE"]:
                        if data["TODATE"] == 'NULL' or data["TODATE"] == '' or data["TODATE"] == '00:00.0' or data["TODATE"] == '  ':
                            value = ''
                        else:
                            value=datetime.datetime.strptime(data["TODATE"], '%d/%m/%Y').strftime("%Y-%m-%d")
                        tdate = value
                        
                    if data["SUPPCODE"]:
                        partner = self.pool.get('res.partner').search(cr,uid,[('supp_code','=',data["SUPPCODE"])])[0]
                    delivey = ''
                        
                    if data["DAYS"]:
                        total_days = data["DAYS"]
                        
                    if data["RETIND"] == 'Y':
                        ret = 'leived'
                    else:
                        ret = 'not_leived'
    
                    ins = 0.0
                    ins_type = 'fix'
                        
                    if data["REMARK"]:
                        note= data["REMARK"]
                        
                    if data["STKRATE"]:
                        rate = data["STKRATE"]
                        
                    if data["ISUQTY"]:
                        qty = data["ISUQTY"]
                        
                    ind_name = ''
                    ind = self.pool.get('indent.indent').search(cr,uid,[('maize','=',name),('contract','=',True)])
                    
                    if ind:
                        ind_name = self.pool.get('indent.indent').read(cr, uid, ind[0],['name'])['name']
                    if data["ITEMCODE"]:
                        product = self.pool.get('product.product').search(cr,uid,[('default_code','=','0'+data["ITEMCODE"])])[0]
                    vals_line = {
                            'product_id':product,
                            'price_unit':float(rate),
                            'name':'test',
                            'product_qty':qty,
                            'product_uom':self.pool.get('product.product').browse(cr,uid,product).uom_id.id,
                            'date_planned':'03/29/2013'
                           }
                    
                    vals = {'name':name,
                            'maize':old_id,
                            'origin':ind_name,
                            'po_series_id':po_series,
                            'date_order':podate,
                            'date_from':fdate,
                            'date_to':tdate,
                            'partner_id': partner,
                            'delivey':delivey,
                            'location_id':12,
                            'pricelist_id':2,
                            'insurance':ins,
                            'insurance_type':ins_type,
                            'no_of_days1':total_days,
                            'total_days':total_days,
                            'retention':ret,
                            'order_line':[(0,0,vals_line)],
                            'notes':note,
                           }
                    data['po'] = po_pool.create(cr, uid, vals, context)
                else:
                    nn = data["JOBSERIES"] + '/' +data["JOBNO"]
                    if nn:
                        po = self.pool.get('purchase.order').search(cr,uid,[('maize','=',nn)])
                    if data["ISUQTY"]:
                        qty = data["ISUQTY"]
                    if data["STKRATE"]:
                        rate = data["STKRATE"]
                    ind_name = ''
                    ind = self.pool.get('indent.indent').search(cr,uid,[('maize','=',name),('contract','=',True)])
                    
                    if ind:
                        ind_name = self.pool.get('indent.indent').read(cr, uid, ind[0],['name'])['name']
                    if data["ITEMCODE"]:
                        product = self.pool.get('product.product').search(cr,uid,[('default_code','=','0'+data["ITEMCODE"])])[0]
                    vals_line = {
                            'product_id':product,
                            'price_unit':float(rate),
                            'name':'test',
                            'product_qty':qty,
                            'product_uom':self.pool.get('product.product').browse(cr,uid,product).uom_id.id,
                            'date_planned':'03/29/2013'
                           }
                    
                    po_pool.write(cr, uid,po[0], {'order_line':[(0,0,vals_line)],}, context)
                    po_pool.write(cr,uid,po[0],{'other_discount':0.1})
                    po_pool.write(cr,uid,po[0],{'other_discount':0.0})
                    
                
            except:
                rejected.append(data['JOBNO'])
                _logger.warning("Skipping Record with Indent code '%s'."%(data['JOBNO']), exc_info=True)
                continue
        print "rejectedrejectedrejected", rejected
        _logger.info("Successfully completed import journal process.")
        return True
    
import_po_contract_data()