import { Injectable } from '@angular/core';

import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';


@Injectable({
  providedIn: 'root'
})
export class ScenarioNewService {

  constructor(private http: HttpClient)
    { }

  private scenarioSettingsBaseURL = 'http://127.0.0.1:8080/scenario-settings';

  getSettingTemporal(): Observable<Setting[]> {
    return this.http.get<Setting[]>(
      `${this.scenarioSettingsBaseURL}/temporal`
    )
  }
}


export class Setting {
  id: number;
  name: string;
}
