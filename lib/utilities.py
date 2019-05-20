
# coding: utf-8

import pandas as pd
import json
import numpy as np
import ast
import os
import operator
from .distance import action_distance, display_distance

def get_dict(dict_str):
    if type(dict_str) is not str:
        return dict_str
    else:
        try:
            return ast.literal_eval(dict_str)
        except:
            print(dict_str)
            return {}


def hack_min(pd_series):
    return np.min(pd_series.dropna())


def hack_max(pd_series):
    return np.max(pd_series.dropna())


INT_OPERATOR_MAP = {
    8: operator.eq,
    32: operator.gt,
    64: operator.ge,
    128: operator.lt,
    256: operator.le,
    512: operator.ne,
}

AGG_MAP = {
    'sum': np.sum,
    'count': len ,
    'min': hack_min,#lambda x:np.nanmin(x.dropna()),
    'max': hack_max,#lambda x:np.nanmax(x.dropna()),
    'avg': np.mean
}

KEYS=[ 'eth_dst', 'eth_src', 'highest_layer', 'info_line',
       'ip_dst', 'ip_src', 'length', 'number',
        'sniff_timestamp', 'tcp_dstport', 'tcp_srcport',
       'tcp_stream']


class Repository:

    def __init__(self, actions_tsv, display_tsv,raw_datasets, schema=KEYS):
        self.actions = pd.read_csv(actions_tsv, sep = '\t', escapechar='\\', keep_default_na=False)
        self.displays = pd.read_csv(display_tsv, sep = '\t', escapechar='\\', keep_default_na=False)
        self.actions.action_params= self.actions.action_params.apply(get_dict)
        #self.actions.bag= self.actions.bag.apply(get_dict)
        self.displays.granularity_layer= self.displays.granularity_layer.apply(get_dict)
        self.displays.data_layer= self.displays.data_layer.apply(get_dict)
        self.schema=schema
        self.data = []
        file_list=os.listdir(raw_datasets)
        file_list.sort()
        for f in file_list:
            path = os.path.join(raw_datasets,f)
            df = pd.read_csv(path, sep = '\t', index_col=0)
            self.data.append(df)


    def get_display_by_id(self, display_id):
        return self.displays[self.displays.display_id == display_id].iloc[0]

    def get_action_by_id(self, action_id):
        return self.actions[self.actions.action_id == action_id].iloc[0]

    def __get_filtered_df(self, project_id, filtering_dict):
    #legacy:
        filters = filtering_dict["list"]
        df = self.data[project_id - 1].copy()
        if filters:
            for filt in filters:
                field = filt["field"]
                op_num = filt["condition"]
                value = filt["term"]
                if op_num in INT_OPERATOR_MAP.keys():
                    opr = INT_OPERATOR_MAP.get(op_num)
                    value= float(value) if df[field].dtype!='O' else value
                    df = df[opr(df[field], value)]
                else:
                    if op_num==16:
                        df = df[df[field].str.contains(value,na=False)]
                    if op_num==2:
                        df = df[df[field].str.startswith(value,na=False)]
                    if op_num==4:
                        df = df[df[field].str.endswith(value,na=False)]
        
        return df
        
    def __get_groupby_df(self, df, grouping_dict, aggregation_dict):
     
        groupings = grouping_dict["list"]
        if aggregation_dict:
            aggregations = aggregation_dict["list"]
            #print(aggregations)
        else:
            aggregations = None
        grouping_attrs = [group["field"] for group in groupings]
        if not grouping_attrs:
            return None,None
        
        df_gb= df.groupby(grouping_attrs)
        
        agg_dict={'number':len} #all group-by gets the count by default in REACT-UI
        if aggregations: #Custom aggregations: sum,count,avg,min,max
            for agg in aggregations:
                agg_dict[agg['field']] = AGG_MAP.get(agg['type'])

            
        agg_df = df_gb.agg(agg_dict)
        return df_gb, agg_df

    def get_raw_display2(self, display_id, pd_group=False):
        row=self.get_display_by_id(display_id)
        raw_df = self.__get_filtered_df(row["project_id"], json.loads(row["filtering"]))
        if type(row["aggregations"]) == float:
            if math.isnan(row["aggregations"]):
                df_gb, agg_df = self.__get_groupby_df(raw_df,json.loads(row["grouping"]), None)
            else:
                df_gb, agg_df = self.__get_groupby_df(raw_df,json.loads(row["grouping"]), json.loads(row["aggregations"]))
        else:
            df_gb, agg_df = self.__get_groupby_df(raw_df,json.loads(row["grouping"]), json.loads(row["aggregations"]))
        if pd_group:
            return raw_df, df_gb
        else:
            return raw_df, agg_df


    def get_raw_display(self, display_id, pd_group=False):
        row=self.get_display_by_id(display_id)
        raw_df = self.__get_filtered_df(row["project_id"], json.loads(row["filtering"]))
        df_gb, agg_df = self.__get_groupby_df(raw_df,json.loads(row["grouping"]), json.loads(row["aggregations"]))
        if pd_group:
            return raw_df, df_gb
        else:
            return raw_df, agg_df

    def __create_action_bag(self,action_id, addType=True):
        action_row= self.get_action_by_id(action_id)
        action_type = action_row.action_type
        action_params = action_row.action_params
        #print(action_params)
        if type(action_params) == str:
            action_params=get_dict(action_params)
        action_bag=set()
        action_bag.add(('type',action_type))
        for k,v in action_params.items():
            if k=='groupPriority':
                continue
            elif k=='aggregations':
                for agg in v:
                    for ak,av in agg.items():
                        if ak=='field':
                            action_bag.add(('agg_field',av))
                        elif ak=='type':
                            action_bag.add(('agg_type',av))
                    
            else:
                action_bag.add((k, v))
        return action_bag

    def display_distance(self,id1, id2):
        d1=self.get_display_by_id(id1)
        d2=self.get_display_by_id(id2)

        dd1={"data_layer": d1.data_layer, "granularity_layer": d1.granularity_layer}
        dd2={"data_layer": d2.data_layer, "granularity_layer": d2.granularity_layer}
        #try:
        return display_distance(dd1,dd2)
        #except:
        #    return None

    def action_distance(self, id1, id2):
        a1 = self.__create_action_bag(id1)
        a2 = self.__create_action_bag(id2)
        try:
            return action_distance(a1, a2)
        except:
            return None
